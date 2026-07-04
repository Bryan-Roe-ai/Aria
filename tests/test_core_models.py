"""Focused tests for core data model primitives."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from core import AgentRegistry as ExportedAgentRegistry
from core import BaseAgent as ExportedBaseAgent
from core import Task as ExportedTask
from core.agent import BaseAgent
from core.registry import AgentRegistry
from core.task import Task


def test_task_defaults_and_validation() -> None:
    task = Task(type="llm", payload={"prompt": "hello"})

    assert task.id
    assert task.priority == 0
    assert task.to_dict()["payload"] == {"prompt": "hello"}

    with pytest.raises(ValueError):
        Task(type="  ")


def test_agent_registry_rejects_duplicate_names() -> None:
    registry = AgentRegistry()

    class _Planner(BaseAgent):
        name = "planner_agent"

        def can_handle(self, task: Task) -> bool:
            return True

        def execute(self, task: Task) -> dict:
            return {"agent": self.name}

    registry.register(_Planner())

    with pytest.raises(ValueError):
        registry.register(_Planner())


def test_core_package_exports_public_api() -> None:
    assert ExportedBaseAgent is BaseAgent
    assert ExportedAgentRegistry is AgentRegistry
    assert ExportedTask is Task


def test_core_module_entrypoint_is_runnable() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "core", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    assert proc.returncode == 0, proc.stderr
    assert "Run Aria core autonomous runtime" in proc.stdout


def test_core_main_can_be_run_directly() -> None:
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[1] / "core" / "__main__.py")],
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
