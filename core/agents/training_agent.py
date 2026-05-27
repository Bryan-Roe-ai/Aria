"""
Training Agent
Handles learning signals, evaluation feedback, and optimization workflows
within the Aria multi-agent runtime.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from core.agent import BaseAgent
from core.task import Task


class TrainingAgent(BaseAgent):
    name = "training_agent"

    def __init__(self) -> None:
        self.buffer = []
        self.performance_history: List[Dict[str, Any]] = []
        self.needs_retraining: bool = False
        self.lora_signal_path = Path("logs") / "lora_signals.jsonl"

    def can_handle(self, task: Task) -> bool:
        return task.type in {"train", "feedback", "evaluate", "optimize"}

    def execute(self, task: Task) -> Dict[str, Any]:
        payload = task.payload or {}
        signal_type = task.type

        self.buffer.append({"type": signal_type, "data": dict(payload)})
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
        if signal_type == "feedback":
            return {"ack": "feedback stored"}

        if signal_type == "train":
            self._dispatch_lora_signal(payload)
            self.needs_retraining = False
            return {"ack": "training signal recorded"}

        if signal_type == "evaluate":
            score = payload.get("score", payload.get("metric", payload.get("value")))
            if isinstance(score, (int, float)):
                numeric_score = float(score)
                self.performance_history.append({"score": numeric_score, "payload": dict(payload)})
                self.needs_retraining = numeric_score < float(payload.get("target_score", 0.7))
                return {
                    "ack": "evaluation logged",
                    "score": numeric_score,
                    "needs_retraining": self.needs_retraining,
                }
            return {"ack": "evaluation logged", "needs_retraining": self.needs_retraining}

        if signal_type == "optimize":
            return {"ack": "optimization queued"}

        return {"ack": "unknown training operation"}

    def _dispatch_lora_signal(self, payload: Dict[str, Any]) -> None:
        self.lora_signal_path.parent.mkdir(parents=True, exist_ok=True)
        record = {"signal": "train", "payload": dict(payload)}
        with self.lora_signal_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def self_assess(self, target_score: float = 0.7) -> Dict[str, Any]:
        latest_score = self.performance_history[-1]["score"] if self.performance_history else None
        if latest_score is not None:
            self.needs_retraining = latest_score < target_score
        return {
            "target_score": target_score,
            "latest_score": latest_score,
            "history_size": len(self.performance_history),
            "needs_retraining": self.needs_retraining,
        }

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
