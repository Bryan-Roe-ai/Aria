"""Task model used by the Aria core runtime."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Task:
    """Structured task envelope for routing and execution."""

    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: int = 0

    def __post_init__(self) -> None:
        """Validate and normalize task fields for stable routing behavior."""
        if not isinstance(self.type, str) or not self.type.strip():
            raise ValueError("Task type must be a non-empty string")
        self.type = self.type.strip()

        if self.payload is None:
            self.payload = {}
        if not isinstance(self.payload, dict):
            raise ValueError("Task payload must be a dictionary")

        if not isinstance(self.priority, int):
            raise ValueError("Task priority must be an integer")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the task."""
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "priority": self.priority,
        }
