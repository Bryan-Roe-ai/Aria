"""Task model used by the lightweight Aria core runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Any, Dict
from uuid import uuid4


@dataclass(slots=True)
class Task:
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time)

    def __post_init__(self) -> None:
        self.type = (self.type or "").strip()
        if not self.type:
            raise ValueError("Task type cannot be empty.")

        self.id = (self.id or str(uuid4())).strip()
        if not isinstance(self.payload, dict):
            raise TypeError("Task payload must be a dictionary.")
        if not isinstance(self.metadata, dict):
            raise TypeError("Task metadata must be a dictionary.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "payload": dict(self.payload),
            "priority": self.priority,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }
