"""Focused tests for core data model primitives."""

from __future__ import annotations

import pytest

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
