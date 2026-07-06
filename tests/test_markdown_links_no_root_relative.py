from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_RELATIVE_LINK_RE = re.compile(r"\[[^\]]+\]\((/[^)\s]*)\)")


def test_markdown_files_do_not_use_root_relative_links() -> None:
    offenders: list[str] = []

    for path in REPO_ROOT.rglob("*.md"):
        rel_path = path.relative_to(REPO_ROOT)
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            match = ROOT_RELATIVE_LINK_RE.search(line)
            if match:
                offenders.append(f"{rel_path}:{line_number}: {match.group(1)}")

    assert not offenders, (
        "Root-relative markdown links break lychee in CI. Use relative paths (./ or ../) or absolute URLs:\n"
        + "\n".join(offenders)
    )
