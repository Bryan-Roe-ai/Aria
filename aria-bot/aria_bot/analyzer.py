"""Repository analyzer.

The analyzer walks the repository (filtered by :class:`RiskManager`) and
emits :class:`Finding` objects describing minor, mechanically-fixable
issues. Findings are intentionally narrow in scope so the executor can
apply them without LLM judgement.

Currently supported finding kinds:

* ``trailing_whitespace`` — lines that end with spaces or tabs.
* ``missing_final_newline`` — files that don't end with a newline.
* ``normalize_line_endings`` — files containing CRLF/CR line endings.
* ``excess_final_newlines`` — files ending with more than one newline.
* ``remove_utf8_bom`` — files that start with a UTF-8 BOM marker.
* ``normalize_unicode_newlines`` — files containing U+2028/U+2029.

Adding a new finding kind requires a matching entry in the executor's
transform table; see :mod:`aria_bot.executor`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from .risk_manager import RiskManager

_logger = logging.getLogger(__name__)

#: Finding kinds the executor knows how to fix. Keep this in sync with
#: :data:`aria_bot.executor.SUPPORTED_KINDS`.
SUPPORTED_KINDS: tuple[str, ...] = (
    "trailing_whitespace",
    "missing_final_newline",
    "normalize_line_endings",
    "excess_final_newlines",
    "remove_utf8_bom",
    "normalize_unicode_newlines",
)


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

    def scan(self, paths: Iterable[Path] | None = None) -> List[Finding]:
        """Return all findings for the requested files (or whole repo)."""

        if paths is None:
            candidates = self.risk_manager.iter_candidate_files(self.suffixes)
        else:
            candidates = [Path(p) for p in paths]

        findings: List[Finding] = []
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
    def _inspect(self, path: Path, data: bytes) -> List[Finding]:
        results: List[Finding] = []
        # Skip likely-binary files. We treat the presence of a NUL byte in
        # the first 4 KiB as a strong binary signal.
        if b"\x00" in data[:4096]:
            return results

        had_utf8_bom = data.startswith(b"\xef\xbb\xbf")
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return results

        if had_utf8_bom:
            results.append(
                Finding(
                    kind="remove_utf8_bom",
                    path=path,
                    detail="file starts with UTF-8 BOM",
                )
            )

        # trailing whitespace
        offending_lines = [i + 1 for i, line in enumerate(text.splitlines()) if line != line.rstrip(" \t")]
        if offending_lines:
            preview = ",".join(str(n) for n in offending_lines[:5])
            results.append(
                Finding(
                    kind="trailing_whitespace",
                    path=path,
                    detail=f"{len(offending_lines)} line(s) (e.g. {preview})",
                )
            )

        # non-LF line endings
        crlf_count = text.count("\r\n")
        lone_cr_count = text.count("\r") - crlf_count
        if crlf_count or lone_cr_count:
            results.append(
                Finding(
                    kind="normalize_line_endings",
                    path=path,
                    detail=f"CRLF={crlf_count}, CR={lone_cr_count}",
                )
            )

        unicode_newlines = text.count("\u2028") + text.count("\u2029")
        if unicode_newlines:
            results.append(
                Finding(
                    kind="normalize_unicode_newlines",
                    path=path,
                    detail=f"{unicode_newlines} unicode newline separator(s)",
                )
            )

        # missing final newline (only meaningful if the file has any content)
        if text and not text.endswith("\n"):
            results.append(
                Finding(
                    kind="missing_final_newline",
                    path=path,
                    detail="file does not end with a newline",
                )
            )

        # more than one trailing newline at EOF
        trailing_newlines = len(text) - len(text.rstrip("\n"))
        if trailing_newlines > 1:
            results.append(
                Finding(
                    kind="excess_final_newlines",
                    path=path,
                    detail=f"{trailing_newlines} trailing newlines",
                )
            )

        return results
