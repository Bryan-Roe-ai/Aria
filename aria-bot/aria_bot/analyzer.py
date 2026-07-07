"""Repository analyzer.

The analyzer walks the repository (filtered by :class:`RiskManager`) and
emits :class:`Finding` objects describing minor, mechanically-fixable
issues. Findings are intentionally narrow in scope so the executor can
apply them without LLM judgement.

Currently supported finding kinds:

* ``utf8_bom`` — files that start with a UTF-8 byte-order mark.
* ``trailing_whitespace`` — lines that end with spaces or tabs.
* ``missing_final_newline`` — files that don't end with a newline.
* ``trailing_blank_lines`` — files that end with extra blank lines.
* ``mixed_line_endings`` — files that use CRLF (``\\r\\n``)
    or lone CR (``\\r``) line endings.

Adding a new finding kind requires a matching entry in the executor's
transform table; see :mod:`aria_bot.executor`.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .registry import SUPPORTED_FINDING_KINDS, TRANSFORM_ORDER
from .risk_manager import RiskManager

_logger = logging.getLogger(__name__)
UTF8_BOM = chr(0xFEFF)

#: Finding kinds the executor knows how to fix. Keep this in sync with
#: :data:`aria_bot.executor.SUPPORTED_KINDS`.
SUPPORTED_KINDS: tuple[str, ...] = SUPPORTED_FINDING_KINDS


@dataclass(frozen=True)
class Finding:
    """A single mechanically-fixable observation about a file."""

    kind: str
    path: Path
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        """Return a serializable representation of the finding."""

        return {
            "kind": self.kind,
            "path": str(self.path),
            "detail": self.detail,
        }


@dataclass
class Analyzer:
    """Scan the repo for safe, mechanically-fixable issues."""

    risk_manager: RiskManager
    suffixes: tuple[str, ...] = (
        ".py",
        ".md",
        ".yaml",
        ".yml",
        ".txt",
        ".json",
        ".toml",
        ".cfg",
        ".ini",
        ".rst",
        ".html",
        ".css",
        ".js",
        ".ts",
    )

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

        for kind in TRANSFORM_ORDER:
            cursor = self._inspect_kind(kind, path, cursor, results)

        return results

    def _inspect_kind(
        self,
        kind: str,
        path: Path,
        cursor: str,
        results: list[Finding],
    ) -> str:
        if kind == "utf8_bom":
            return self._inspect_utf8_bom(path, cursor, results)
        if kind == "mixed_line_endings":
            return self._inspect_mixed_line_endings(path, cursor, results)
        if kind == "trailing_whitespace":
            return self._inspect_trailing_whitespace(path, cursor, results)
        if kind == "trailing_blank_lines":
            return self._inspect_trailing_blank_lines(path, cursor, results)
        if kind == "missing_final_newline":
            return self._inspect_missing_final_newline(path, cursor, results)
        return cursor

    def _inspect_utf8_bom(
        self,
        path: Path,
        cursor: str,
        results: list[Finding],
    ) -> str:
        if cursor.startswith(UTF8_BOM):
            detail: str = "file starts with a UTF-8 BOM"
            results.append(
                Finding(
                    kind="utf8_bom",
                    path=path,
                    detail=detail,
                )
            )
            return cursor[1:]
        return cursor

    def _inspect_mixed_line_endings(
        self,
        path: Path,
        cursor: str,
        results: list[Finding],
    ) -> str:
        # Stage 1a: CRLF → LF (must happen before lone-CR detection).
        crlf_count = cursor.count("\r\n")
        if crlf_count:
            cursor = cursor.replace("\r\n", "\n")

        # Stage 1b: lone CR → LF (old Mac-style line endings).
        lone_cr_count = cursor.count("\r")
        if not crlf_count and not lone_cr_count:
            return cursor

        if lone_cr_count:
            cursor = cursor.replace("\r", "\n")

        parts: list[str] = []
        if crlf_count:
            parts.append(f"{crlf_count} CRLF")
        if lone_cr_count:
            parts.append(f"{lone_cr_count} lone CR")

        detail: str = f"{', '.join(parts)} line ending(s)"
        results.append(
            Finding(
                kind="mixed_line_endings",
                path=path,
                detail=detail,
            )
        )
        return cursor

    def _inspect_trailing_whitespace(
        self,
        path: Path,
        cursor: str,
        results: list[Finding],
    ) -> str:
        lines = cursor.split("\n")
        offending_lines = [index + 1 for index, line in enumerate(lines) if line != line.rstrip(" \t")]
        if not offending_lines:
            return cursor

        preview = ",".join(str(number) for number in offending_lines[:5])
        detail: str = f"{len(offending_lines)} line(s) (e.g. {preview})"
        results.append(
            Finding(
                kind="trailing_whitespace",
                path=path,
                detail=detail,
            )
        )
        return "\n".join(line.rstrip(" \t") for line in lines)

    def _inspect_trailing_blank_lines(
        self,
        path: Path,
        cursor: str,
        results: list[Finding],
    ) -> str:
        if not cursor:
            return cursor

        trailing_newlines = len(cursor) - len(cursor.rstrip("\n"))
        if trailing_newlines <= 1:
            return cursor

        detail: str = f"{trailing_newlines - 1} extra blank line(s) at EOF"
        results.append(
            Finding(
                kind="trailing_blank_lines",
                path=path,
                detail=detail,
            )
        )
        return cursor.rstrip("\n") + "\n"

    def _inspect_missing_final_newline(
        self,
        path: Path,
        cursor: str,
        results: list[Finding],
    ) -> str:
        if cursor and not cursor.endswith("\n"):
            detail: str = "file does not end with a newline"
            results.append(
                Finding(
                    kind="missing_final_newline",
                    path=path,
                    detail=detail,
                )
            )
        return cursor
