from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = REPO_ROOT / ".vscode" / "tasks.json"
LAUNCH_PATH = REPO_ROOT / ".vscode" / "launch.json"
MAKEFILE_PATH = REPO_ROOT / "Makefile"


def _load_json(path: Path) -> dict:
    assert path.exists(), f"Expected {path} to exist"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.unit
def test_launch_json_contains_aria_bot_debug_profiles() -> None:
    launch = _load_json(LAUNCH_PATH)
    names = {config.get("name") for config in launch.get("configurations", [])}

    assert "Python Debugger: aria-bot (dry-run)" in names
    assert "Python Debugger: aria-bot (apply)" in names


@pytest.mark.unit
def test_tasks_json_contains_aria_bot_tasks() -> None:
    tasks = _load_json(TASKS_PATH)
    labels = {task.get("label") for task in tasks.get("tasks", [])}

    assert "aria-bot: dry-run" in labels
    assert "aria-bot: apply" in labels
    assert "aria-bot: test-suite" in labels


@pytest.mark.unit
def test_makefile_contains_aria_bot_targets() -> None:
    content = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "aria-bot:" in content
    assert "aria-bot-apply:" in content
    assert "test-aria-bot:" in content
