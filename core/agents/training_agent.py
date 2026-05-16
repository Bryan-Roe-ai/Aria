"""
Training Agent
Handles learning signals, evaluation feedback, and optimization workflows
within the Aria multi-agent runtime.
"""

from __future__ import annotations

from typing import Dict, Any
from core.agent import BaseAgent
from core.task import Task


class TrainingAgent(BaseAgent):
    name = "training_agent"

    def __init__(self):
        self.buffer = []  # stores feedback / training samples

    def can_handle(self, task: Task) -> bool:
        return task.type in {"train", "feedback", "evaluate", "optimize"}

    def execute(self, task: Task) -> Dict[str, Any]:
        payload = task.payload or {}
        signal_type = task.type

        # Store experience
        self.buffer.append(
            {
                "type": signal_type,
                "data": dict(payload),
            }
        )

        result = self._process(signal_type, payload)

        return {
            "agent": self.name,
            "task_id": task.id,
            "status": "recorded",
            "result": result,
            "buffer_size": len(self.buffer),
            "summary": self.summary(),
        }

    def _process(self, signal_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for future optimization / fine-tuning logic
        if signal_type == "feedback":
            return {"ack": "feedback stored"}

        if signal_type == "train":
            return {"ack": "training signal recorded"}

        if signal_type == "evaluate":
            return {"ack": "evaluation logged"}

        if signal_type == "optimize":
            return {"ack": "optimization queued"}

        return {"ack": "unknown training operation"}

    def summary(self) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for entry in self.buffer:
            signal_type = entry.get("type", "unknown")
            counts[signal_type] = counts.get(signal_type, 0) + 1
        latest = self.buffer[-1] if self.buffer else None
        return {
            "total_signals": len(self.buffer),
            "counts": counts,
            "latest_signal": latest.get("type") if latest else None,
        }
