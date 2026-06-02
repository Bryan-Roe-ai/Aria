"""Repository analyzer.

The analyzer walks the repository (filtered by :class:`RiskManager`) and
emits :class:`Finding` objects describing minor, mechanically-fixable
issues. Findings are intentionally narrow in scope so the executor can
apply them without LLM judgement.

Currently supported finding kinds:

* ``trailing_whitespace`` — lines that end with spaces or tabs.
* ``missing_final_newline`` — files that don't end with a newline.
* ``trailing_blank_lines`` — files that end with extra blank lines.
* ``mixed_line_endings`` — files that mix CRLF (``\\r\\n``) and LF line endings.

Adding a new finding kind requires a matching entry in the executor's
transform table; see :mod:`aria_bot.executor`.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from .registry import SUPPORTED_FINDING_KINDS
from .risk_manager import RiskManager

_logger = logging.getLogger(__name__)

#: Finding kinds the executor knows how to fix. Keep this in sync with
#: :data:`aria_bot.executor.SUPPORTED_KINDS`.
SUPPORTED_KINDS: tuple[str, ...] = SUPPORTED_FINDING_KINDS


@dataclass(frozen=True)
class Finding:
    """A single mechanically-fixable observation about a file."""

    kind: str
    path: Path
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "path": str(self.path),
            "detail": self.detail,
        }


@dataclass
class Analyzer:
    """Scan the repo for safe, mechanically-fixable issues."""

    risk_manager: RiskManager
    suffixes: Sequence[str] = (".py", ".md", ".yaml", ".yml", ".txt")

    def scan(self, paths: Iterable[Path] | None = None) -> list[Finding]:
        """Return all findings for the requested files (or whole repo)."""

        if paths is None:
            candidates = self.risk_manager.iter_candidate_files(self.suffixes)
        else:
            candidates = [Path(p) for p in paths]

        findings: list[Finding] = []
        for path in candidates:
            assessment = self.risk_manager.assess_file(path)
            if not assessment.allowed:
                _logger.debug("skipping %s: %s", path, assessment.reasons)
                continue
            try:
                data = path.read_bytes()
            except OSError as exc:
                _logger.debug("unable to read %s: %s", path, exc)
                continue
            findings.extend(self._inspect(path, data))
        return findings

    # ------------------------------------------------------------------
    # Per-file inspections
    # ------------------------------------------------------------------
    def _inspect(self, path: Path, data: bytes) -> list[Finding]:
        results: list[Finding] = []
        # Skip likely-binary files. We treat the presence of a NUL byte in
        # the first 4 KiB as a strong binary signal.
        if b"\x00" in data[:4096]:
            return results

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return results

        # Detection mirrors the executor's canonical transform order so that
        # every finding reflects a change the executor will actually make,
        # and so applying all fixes for a file converges in a *single* pass.
        # Each stage inspects the text as it would be *after* the previous
        # stages' transforms have run. This is essential for idempotency:
        # stripping a trailing-whitespace-only line (``"x\n   \n"``) or
        # normalizing CRLF blank lines can expose trailing blank lines that a
        # naive raw-text check would miss until the next cycle.
        cursor = text

        # Stage 1: normalize CRLF line endings to LF.
        if "\r\n" in cursor:
            crlf_count = cursor.count("\r\n")
            results.append(
                Finding(
                    kind="mixed_line_endings",
                    path=path,
                    detail=f"{crlf_count} CRLF line ending(s)",
                )
            )
            cursor = cursor.replace("\r\n", "\n")

        # Stage 2: strip per-line trailing whitespace (on LF-normalized text).
        offending_lines = [i + 1 for i, line in enumerate(cursor.split("\n")) if line != line.rstrip(" \t")]
        if offending_lines:
            preview = ",".join(str(n) for n in offending_lines[:5])
            results.append(
                Finding(
                    kind="trailing_whitespace",
                    path=path,
                    detail=f"{len(offending_lines)} line(s) (e.g. {preview})",
                )
            )
            cursor = "\n".join(line.rstrip(" \t") for line in cursor.split("\n"))

        # Stage 3: trim extra blank lines at EOF (on whitespace-stripped text)
        # down to exactly one terminal newline.
        if cursor:
            trailing_newlines = len(cursor) - len(cursor.rstrip("\n"))
            if trailing_newlines > 1:
                results.append(
                    Finding(
                        kind="trailing_blank_lines",
                        path=path,
                        detail=f"{trailing_newlines - 1} extra blank line(s) at EOF",
                    )
                )
                cursor = cursor.rstrip("\n") + "\n"

        # Stage 4: ensure a single final newline (non-empty content only).
        if cursor and not cursor.endswith("\n"):
            results.append(
                Finding(
                    kind="missing_final_newline",
                    path=path,
                    detail="file does not end with a newline",
                )
            )

        return results
