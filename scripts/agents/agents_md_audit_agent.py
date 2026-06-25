"""Audit AGENTS.md learned-memory sections for structure and hygiene."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORT))

from scripts.agents.base import REPO_ROOT, AgentResult, AutomationAgent, register  # noqa: E402

LEARNED_SECTIONS = (
    "## Learned User Preferences",
    "## Learned Workspace Facts",
)
MAX_BULLETS_PER_SECTION = 12
MIN_BULLETS_PER_SECTION = 1
STALE_DATE_DAYS = 30

MERGE_CONFLICT_PATTERN = re.compile(r"^(<<<<<<<|=======|>>>>>>>)")
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9]{10,}\b"),
    re.compile(r"\bpassword\s*=\s*\S+", re.IGNORECASE),
    re.compile(r"\bapi[_-]?key\s*=\s*\S+", re.IGNORECASE),
)
DATE_PATTERN = re.compile(
    r"\b(?:as of|updated|since)\s+(\d{4}-\d{2}-\d{2})\b",
    re.IGNORECASE,
)


@register
class AgentsMdAuditAgent(AutomationAgent):
    """Validate AGENTS.md learned-memory sections for structure and hygiene."""

    name = "agents-md-audit"
    description = "Validates AGENTS.md Learned sections for structure, bullet limits, and secret patterns."

    def __init__(
        self,
        repo_root: Path | None = None,
        *,
        agents_md_path: Path | None = None,
        stale_date_days: int = STALE_DATE_DAYS,
    ) -> None:
        super().__init__(repo_root=repo_root)
        self.agents_md_path = (
            Path(agents_md_path) if agents_md_path is not None else self.repo_root / "AGENTS.md"
        )
        self.stale_date_days = stale_date_days

    def run(self) -> AgentResult:
        """Audit AGENTS.md learned sections and return structured findings."""
        findings: list[dict] = []
        metrics: dict = {
            "sections_found": 0,
            "preferences_bullets": 0,
            "facts_bullets": 0,
            "stale_dates": 0,
        }

        if not self.agents_md_path.exists():
            findings.append(
                {
                    "kind": "missing_file",
                    "file": self._relative_path(self.agents_md_path),
                    "message": "AGENTS.md not found",
                }
            )
            return self._finish(findings, metrics)

        try:
            content = self.agents_md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(
                {
                    "kind": "read_error",
                    "file": self._relative_path(self.agents_md_path),
                    "message": str(exc),
                }
            )
            return self._finish(findings, metrics)

        self._check_merge_conflicts(content, findings)
        section_bullets = self._parse_sections(content, findings)
        metrics["sections_found"] = len(section_bullets)

        for section_title, bullets in section_bullets.items():
            bullet_count = len(bullets)
            if section_title == LEARNED_SECTIONS[0]:
                metrics["preferences_bullets"] = bullet_count
            elif section_title == LEARNED_SECTIONS[1]:
                metrics["facts_bullets"] = bullet_count

            if bullet_count < MIN_BULLETS_PER_SECTION:
                findings.append(
                    {
                        "kind": "empty_section",
                        "section": section_title,
                        "message": f"Section has {bullet_count} bullets; expected at least {MIN_BULLETS_PER_SECTION}.",
                    }
                )
            elif bullet_count > MAX_BULLETS_PER_SECTION:
                findings.append(
                    {
                        "kind": "bullet_limit",
                        "section": section_title,
                        "message": (
                            f"Section has {bullet_count} bullets; "
                            f"maximum allowed is {MAX_BULLETS_PER_SECTION}."
                        ),
                    }
                )

            for index, bullet in enumerate(bullets, start=1):
                self._check_bullet_hygiene(section_title, index, bullet, findings, metrics)

        return self._finish(findings, metrics)

    def _finish(self, findings: list[dict], metrics: dict) -> AgentResult:
        has_error = any(f["kind"] in {"missing_file", "read_error", "missing_section"} for f in findings)
        has_warning = bool(findings) and not has_error
        status = "error" if has_error else ("warning" if has_warning else "ok")
        summary = (
            f"Audited {self._relative_path(self.agents_md_path)}: "
            f"{metrics.get('preferences_bullets', 0)} preference bullets, "
            f"{metrics.get('facts_bullets', 0)} fact bullets, "
            f"{len(findings)} finding{'s' if len(findings) != 1 else ''}."
        )
        return self.make_result(status=status, summary=summary, findings=findings, metrics=metrics)

    def _check_merge_conflicts(self, content: str, findings: list[dict]) -> None:
        for line_number, line in enumerate(content.splitlines(), start=1):
            if MERGE_CONFLICT_PATTERN.match(line.strip()):
                findings.append(
                    {
                        "kind": "merge_conflict",
                        "line": line_number,
                        "message": "Merge conflict marker detected",
                        "text": line.strip(),
                    }
                )

    def _parse_sections(self, content: str, findings: list[dict]) -> dict[str, list[str]]:
        lines = content.splitlines()
        section_starts: dict[str, int] = {}
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped in LEARNED_SECTIONS:
                section_starts[stripped] = index

        for section_title in LEARNED_SECTIONS:
            if section_title not in section_starts:
                findings.append(
                    {
                        "kind": "missing_section",
                        "section": section_title,
                        "message": f"Required section {section_title!r} not found.",
                    }
                )

        section_bullets: dict[str, list[str]] = {}
        ordered_sections = sorted(section_starts.items(), key=lambda item: item[1])
        for position, (section_title, start_index) in enumerate(ordered_sections):
            end_index = (
                ordered_sections[position + 1][1]
                if position + 1 < len(ordered_sections)
                else len(lines)
            )
            bullets: list[str] = []
            for line in lines[start_index + 1 : end_index]:
                stripped = line.strip()
                if stripped.startswith("- "):
                    bullets.append(stripped[2:].strip())
                elif stripped.startswith("## "):
                    break
            section_bullets[section_title] = bullets

        return section_bullets

    def _check_bullet_hygiene(
        self,
        section_title: str,
        index: int,
        bullet: str,
        findings: list[dict],
        metrics: dict,
    ) -> None:
        for pattern in SECRET_PATTERNS:
            if pattern.search(bullet):
                findings.append(
                    {
                        "kind": "secret_pattern",
                        "section": section_title,
                        "bullet_index": index,
                        "message": "Possible secret or credential pattern in bullet text.",
                    }
                )

        for match in DATE_PATTERN.finditer(bullet):
            date_text = match.group(1)
            try:
                referenced = datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            age_days = (datetime.now(timezone.utc) - referenced).days
            if age_days > self.stale_date_days:
                metrics["stale_dates"] += 1
                findings.append(
                    {
                        "kind": "stale_date",
                        "section": section_title,
                        "bullet_index": index,
                        "message": f"Referenced date {date_text} is {age_days} days old.",
                        "text": bullet[:200],
                    }
                )

    def _relative_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.repo_root))
        except ValueError:
            return str(path)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the AGENTS.md audit agent."""
    parser = argparse.ArgumentParser(description=AgentsMdAuditAgent.description)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root (default: repo root).")
    parser.add_argument(
        "--agents-md",
        type=Path,
        default=None,
        help="Path to AGENTS.md (default: <root>/AGENTS.md).",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=STALE_DATE_DAYS,
        help=f"Warn when referenced dates exceed this many days (default: {STALE_DATE_DAYS}).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Compute results without writing status.json.")
    parser.add_argument("--json", action="store_true", help="Print the full result as JSON.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the AGENTS.md audit CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    agents_md_path = args.agents_md if args.agents_md is not None else args.root / "AGENTS.md"
    agent = AgentsMdAuditAgent(
        repo_root=args.root,
        agents_md_path=agents_md_path,
        stale_date_days=args.stale_days,
    )
    result = agent.run()

    if not args.dry_run:
        agent.write_status(result)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.summary)

    return 1 if result.status == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
