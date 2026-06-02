from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = REPO_ROOT / ".vscode" / "tasks.json"
SERVICE_PATH = REPO_ROOT / "config" / "aria-agi-launcher.service"
LAUNCHER_PATH = REPO_ROOT / "scripts" / "startup_agi.sh"

AGI_INPUT_DEFAULTS = {
    "agiCycles": "1",
    "agiShortBreakSec": "30",
    "agiLongBreakSec": "300",
    "agiLongBreakEvery": "5",
}


def _load_tasks() -> dict:
    assert TASKS_PATH.exists(), "Expected .vscode/tasks.json to exist"
    return json.loads(TASKS_PATH.read_text(encoding="utf-8"))


def _task_by_label(tasks: dict, label: str) -> dict:
    matches = [t for t in tasks.get("tasks", []) if t.get("label") == label]
    assert matches, f"Expected a task labelled {label!r}"
    return matches[0]


def _command_string(task: dict) -> str:
    return " ".join(task.get("args", []))


@pytest.mark.unit
def test_tasks_json_is_valid_json() -> None:
    _load_tasks()


@pytest.mark.unit
def test_startup_agi_inputs_defined_with_defaults() -> None:
    tasks = _load_tasks()
    inputs = {i["id"]: i for i in tasks.get("inputs", [])}
    for input_id, default in AGI_INPUT_DEFAULTS.items():
        assert input_id in inputs, f"Missing input {input_id!r}"
        assert inputs[input_id]["type"] == "promptString"
        assert inputs[input_id]["default"] == default


@pytest.mark.unit
def test_startup_agi_task_wires_all_options() -> None:
    tasks = _load_tasks()
    command = _command_string(_task_by_label(tasks, "startup: agi"))
    assert "bash scripts/startup_agi.sh" in command
    assert "--cycles ${input:agiCycles}" in command
    assert "--short-break-sec ${input:agiShortBreakSec}" in command
    assert "--long-break-sec ${input:agiLongBreakSec}" in command
    assert "--long-break-every ${input:agiLongBreakEvery}" in command


@pytest.mark.unit
def test_service_tasks_exist() -> None:
    tasks = _load_tasks()
    for label in (
        "service: agi install",
        "service: agi start",
        "service: agi stop",
        "service: agi status",
    ):
        _task_by_label(tasks, label)


@pytest.mark.unit
def test_service_install_and_start_guard_against_missing_systemd() -> None:
    tasks = _load_tasks()
    for label in ("service: agi install", "service: agi start"):
        command = _command_string(_task_by_label(tasks, label))
        assert "${XDG_RUNTIME_DIR:-/nonexistent}/systemd/private" in command
        assert "startup: agi" in command, "Guard should point users to the startup: agi task"


@pytest.mark.unit
def test_service_install_targets_user_unit_directory() -> None:
    tasks = _load_tasks()
    command = _command_string(_task_by_label(tasks, "service: agi install"))
    assert "config/aria-agi-launcher.service" in command
    assert "$HOME/.config/systemd/user" in command
    assert "systemctl --user enable aria-agi-launcher.service" in command


@pytest.mark.unit
def test_service_unit_file_is_a_well_formed_user_service() -> None:
    assert SERVICE_PATH.exists(), "Expected config/aria-agi-launcher.service to exist"
    content = SERVICE_PATH.read_text(encoding="utf-8")
    assert "[Unit]" in content
    assert "[Service]" in content
    assert "[Install]" in content
    # User services install under default.target, not multi-user.target.
    assert "WantedBy=default.target" in content
    assert "scripts/startup_agi.sh" in content
    # StartLimit* keys belong in [Unit] for modern systemd.
    unit_section = content.split("[Service]", 1)[0]
    assert "StartLimitIntervalSec=" in unit_section
    assert "StartLimitBurst=" in unit_section


@pytest.mark.unit
def test_service_unit_defaults_to_infinite_cycles() -> None:
    content = SERVICE_PATH.read_text(encoding="utf-8")
    assert "AGI_LAUNCH_CYCLES=0" in content


@pytest.mark.unit
def test_launcher_script_supports_wired_flags() -> None:
    assert LAUNCHER_PATH.exists(), "Expected scripts/startup_agi.sh to exist"
    content = LAUNCHER_PATH.read_text(encoding="utf-8")
    for flag in ("--cycles", "--short-break-sec", "--long-break-sec", "--long-break-every"):
        assert flag in content, f"Launcher should support {flag}"
