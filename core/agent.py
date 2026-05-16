"""Shared base contract for the lightweight Aria core agent runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from core.task import Task


class BaseAgent(ABC):
    """Minimal runtime contract shared by core agents."""

    name = "base_agent"

    @abstractmethod
    def can_handle(self, task: Task) -> bool:
        """Return True when this agent can execute the given task."""

    @abstractmethod
    def execute(self, task: Task) -> Dict[str, Any]:
        """Execute the task and return a structured result."""

    def describe(self) -> Dict[str, Any]:
        return {"name": self.name, "class": self.__class__.__name__}
