"""Verify the repository tree contains no orphaned gitlinks.

An orphaned gitlink is a tree entry with mode 160000 (submodule commit) that
has no corresponding ``[submodule "<path>"]`` block in ``.gitmodules``.

When such an entry exists, ``git submodule foreach --recursive`` — run by
``actions/checkout`` during credential cleanup — fails with::

    fatal: No url found for submodule path '<path>' in .gitmodules

This caused CI job 84021614545 ("Generate Training Health Report") to fail
when ``LMStudio-MCP`` was committed as a gitlink without a .gitmodules entry.

The test runs ``git ls-files --stage`` locally, so it reflects uncommitted
working-tree additions as well as committed ones.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _get_gitlink_paths() -> list[str]:
    """Return paths of all gitlinks (mode 160000) in the current index."""
    result = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    paths = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "160000":
            paths.append(parts[3])
    return paths


def _get_gitmodules_paths() -> set[str]:
    """Return the set of submodule paths declared in .gitmodules."""
    gitmodules = REPO_ROOT / ".gitmodules"
    if not gitmodules.exists():
        return set()
    paths: set[str] = set()
    for line in gitmodules.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("path"):
            _, _, value = line.partition("=")
            paths.add(value.strip())
    return paths


def test_no_orphaned_gitlinks() -> None:
    """Every gitlink in the index must have a .gitmodules entry with a URL."""
    gitlinks = _get_gitlink_paths()
    declared = _get_gitmodules_paths()

    orphans = [p for p in gitlinks if p not in declared]
    assert not orphans, (
        "Orphaned gitlinks found (present in index but missing from .gitmodules):\n"
        + "\n".join(f"  {p}" for p in orphans)
        + "\n\nFix: either add a '[submodule \"<path>\"]' block with a 'url =' to "
        ".gitmodules, or remove the gitlink with 'git rm <path>'.\n"
        "See CI job 84021614545 for the failure this causes in actions/checkout."
    )
