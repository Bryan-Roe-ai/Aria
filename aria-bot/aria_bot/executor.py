"""Executor — apply :class:`UpgradePlan` objects to the filesystem.

The executor is intentionally tiny: every supported finding kind maps to a
pure, in-memory text transform. The transformed bytes are then re-checked
by the :class:`RiskManager` before being written to disk. If anything
looks wrong we abort the plan and leave the file untouched.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

from .planner import UpgradePlan
from .registry import SUPPORTED_FINDING_KINDS, TRANSFORM_ORDER
from .risk_manager import RiskManager

_logger = logging.getLogger(__name__)

# Each transform takes the file text and returns the rewritten text.
Transform = Callable[[str], str]


def _py_parses(text: str, filename: str) -> bool:
    """Return True if ``text`` is syntactically valid Python.

    Uses :func:`compile` (which never executes code) purely as a parse check.
    Non-syntax ``ValueError`` cases (e.g. embedded NUL bytes) are treated as
    "cannot judge" and reported as parseable so we don't block on them.
    """

    try:
        compile(text, filename, "exec", dont_inherit=True)
    except SyntaxError:
        return False
    except ValueError:
        return True
    return True


def _strip_utf8_bom(text: str) -> str:
    """Remove a leading UTF-8 BOM (U+FEFF) if present."""
    if text.startswith("\ufeff"):
        return text[1:]
    return text


def _strip_trailing_whitespace(text: str) -> str:
    # Preserve the original line endings (LF only here — repo is LF).
    return "\n".join(line.rstrip(" \t") for line in text.split("\n"))


def _ensure_final_newline(text: str) -> str:
    if not text:
        return text
    return text if text.endswith("\n") else text + "\n"


def _trim_trailing_blank_lines(text: str) -> str:
    if not text:
        return text
    return text.rstrip("\n") + "\n"


def _normalize_line_endings(text: str) -> str:
    """Replace all CRLF and lone CR sequences with LF."""
    # CRLF first, then remaining lone CRs (old Mac-style).
    return text.replace("\r\n", "\n").replace("\r", "\n")


_TRANSFORMS: dict[str, Transform] = {
    "utf8_bom": _strip_utf8_bom,
    "trailing_whitespace": _strip_trailing_whitespace,
    "missing_final_newline": _ensure_final_newline,
    "trailing_blank_lines": _trim_trailing_blank_lines,
    "mixed_line_endings": _normalize_line_endings,
}

#: Finding kinds the executor knows how to apply. Keep this in sync with
#: :data:`aria_bot.analyzer.SUPPORTED_KINDS`.
SUPPORTED_KINDS: tuple[str, ...] = tuple(sorted(SUPPORTED_FINDING_KINDS))

# Fail fast if a transform is ever added without a defined application order.
assert set(TRANSFORM_ORDER) == set(_TRANSFORMS), "TRANSFORM_ORDER must cover every transform"


@dataclass
class ExecutionResult:
    """Outcome of executing a single :class:`UpgradePlan`."""

    plan: UpgradePlan
    applied: bool
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "path": str(self.plan.path),
            "kinds": list(self.plan.kinds),
            "applied": self.applied,
            "reason": self.reason,
        }


@dataclass
class Executor:
    """Apply upgrade plans, with optional dry-run."""

    risk_manager: RiskManager
    dry_run: bool = True

    def execute(self, plans: Sequence[UpgradePlan]) -> list[ExecutionResult]:
        results: list[ExecutionResult] = []
        for plan in plans:
            results.append(self._execute_one(plan))
        return results

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _execute_one(self, plan: UpgradePlan) -> ExecutionResult:
        path = plan.path

        # Final path-level safety check — never trust the planner alone.
        path_assessment = self.risk_manager.assess_file(path)
        if not path_assessment.allowed:
            return ExecutionResult(plan=plan, applied=False, reason="; ".join(path_assessment.reasons))

        unsupported = [k for k in plan.kinds if k not in _TRANSFORMS]
        if unsupported:
            return ExecutionResult(
                plan=plan,
                applied=False,
                reason=f"unsupported transform(s): {','.join(unsupported)}",
            )

        try:
            original = path.read_bytes()
        except OSError as exc:
            return ExecutionResult(plan=plan, applied=False, reason=f"read failed: {exc}")

        # Apply each transform in a deterministic order.
        try:
            text = original.decode("utf-8")
        except UnicodeDecodeError:
            return ExecutionResult(plan=plan, applied=False, reason="file is not valid UTF-8")

        # Apply transforms in the canonical order (not plan.kinds order),
        # so combined application is deterministic and converges in one pass.
        ordered_kinds = [k for k in TRANSFORM_ORDER if k in plan.kinds]
        new_text = text
        for kind in ordered_kinds:
            new_text = _TRANSFORMS[kind](new_text)
        new_bytes = new_text.encode("utf-8")

        # Syntax safety net: if the original Python file parsed but our edit
        # would break it, abort. This is diff-scoped and false-positive-free —
        # we never blame the bot for pre-existing syntax errors. Whitespace
        # transforms never trip this; it guards future, less-trivial transforms.
        if path.suffix == ".py" and _py_parses(text, str(path)) and not _py_parses(new_text, str(path)):
            return ExecutionResult(
                plan=plan,
                applied=False,
                reason="transform would introduce a Python syntax error",
            )

        # Diff-level safety: re-check size delta and require an actual change.
        change_assessment = self.risk_manager.assess_change(path, original, new_bytes)
        if not change_assessment.allowed:
            return ExecutionResult(plan=plan, applied=False, reason="; ".join(change_assessment.reasons))

        if self.dry_run:
            _logger.info("[dry-run] would update %s (%s)", path, plan.description())
            return ExecutionResult(plan=plan, applied=False, reason="dry-run")

        try:
            path.write_bytes(new_bytes)
        except OSError as exc:
            return ExecutionResult(plan=plan, applied=False, reason=f"write failed: {exc}")

        _logger.info("updated %s (%s)", path, plan.description())
        return ExecutionResult(plan=plan, applied=True, reason="ok")
