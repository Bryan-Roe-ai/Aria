"""Verify .gitignore contains recursive venv rules and practical matches."""

from __future__ import annotations

import subprocess
from pathlib import Path

REQUIRED_PATTERNS = ("**/.venv/", "**/venv/")


def _gitignore_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_required_patterns(text: str) -> bool:
    return all(pattern in text for pattern in REQUIRED_PATTERNS)


def _check_ignore_matches() -> bool:
    probe_paths = [
        ".venv/bin/python",
        "apps/aria/venv/bin/python",
        "ai-projects/chat-cli/.venv/bin/python",
        "deep/nested/venv/lib/site.py",
    ]
    probe_input = "\n".join(probe_paths) + "\n"
    result = subprocess.run(
        ["git", "check-ignore", "-v", "--stdin"],
        input=probe_input,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("❌ .gitignore not found.")
        return 1

    text = _gitignore_text(gitignore_path)
    has_patterns = _has_required_patterns(text)
    print(f"has_recursive_patterns={has_patterns}")
    if not has_patterns:
        print("❌ Missing required recursive venv ignore patterns.")
        return 1

    matches_ok = _check_ignore_matches()
    print(f"git_check_ignore_matches={matches_ok}")
    if not matches_ok:
        print("❌ git check-ignore did not match probe paths.")
        return 1

    print("✅ Recursive venv ignore verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
