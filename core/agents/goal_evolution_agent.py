"""
Goal Evolution Agent
Generates and refines goals based on memory history for autonomous operation.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Sequence

from core.agent import BaseAgent
from core.llm.client import LLMClient
from core.memory.store import MemoryStore
from core.task import Task

logger = logging.getLogger(__name__)


class GoalEvolutionAgent(BaseAgent):
    """Agent that proposes and refines goals using memory context and an LLM."""

    name = "goal_evolution_agent"

    def __init__(
        self,
        memory: MemoryStore,
        llm: LLMClient | None = None,
        goal_horizon: str = "medium_term",
    ) -> None:
        self.memory = memory
        self.llm = llm or LLMClient()
        self.goal_horizon = goal_horizon

    def can_handle(self, task: Task) -> bool:
        return task.type in {"goal_evolve", "new_goal", "reflect"}

    def execute(self, task: Task) -> dict[str, object]:
        payload = task.payload or {}
        history = self.memory.last(30)
        horizon = str(payload.get("horizon") or self.goal_horizon)
        prompt = self._build_prompt(history, horizon)

        messages = [
            {
                "role": "system",
                "content": "You are a goal evolution engine. Output ONLY a JSON object with a single field: goal.",
            },
            {"role": "user", "content": prompt},
        ]

        raw = ""
        try:
            raw = self.llm.complete(messages)
        except Exception as exc:
            logger.exception("LLM client failed while generating goal: %s", exc)

        goal = self._parse(raw)

        try:
            self.memory.write("goal_evolved", {"goal": goal, "goal_horizon": horizon})
        except Exception:
            logger.exception("Memory write failed when storing evolved goal")

        return {"agent": self.name, "goal": goal, "task_id": task.id, "goal_horizon": horizon}

    def _build_prompt(self, history: Sequence[dict[str, object]], horizon: str) -> str:
        horizon_map = {
            "short": "Focus on immediate next actions and quick wins.",
            "short_term": "Focus on immediate next actions and quick wins.",
            "medium": "Balance near-term execution with mid-term improvement.",
            "medium_term": "Balance near-term execution with mid-term improvement.",
            "long": "Favor strategic, longer-horizon system evolution.",
            "long_term": "Favor strategic, longer-horizon system evolution.",
        }
        prefix = horizon_map.get(horizon.lower(), f"Use a {horizon} planning horizon.")
        if not history:
            return f"{prefix}\nNo history. Generate a simple useful system improvement goal."

        entries = history[-10:]
        summary_parts = []
        for event in entries:
            event_type = event.get("type", "event")
            data = event.get("data")
            if isinstance(data, dict):
                short = data.get("goal") or data.get("message") or data.get("output")
            else:
                short = str(data)[:80] if data is not None else ""
            summary_parts.append(f"{event_type}: {short}" if short else str(event_type))

        summary = " | ".join(summary_parts)
        return (
            f"{prefix}\n"
            f"Based on system history:\n{summary}\n\n"
            "Generate the next most useful goal for system improvement, learning, or optimization."
        )

    def _parse(self, raw: str) -> str:
        fallback = "improve system performance"

        if not raw or not raw.strip():
            logger.debug("Empty LLM response for goal evolution; returning fallback")
            return fallback

        try:
            data = json.loads(raw)
            if isinstance(data, dict) and "goal" in data:
                goal = str(data.get("goal", fallback)).strip()
                return self._normalize_goal(goal, fallback)
        except Exception:
            logger.debug("Strict JSON parsing failed for LLM output; attempting substring search")

        try:
            match = re.search(r"\{.*?\}", raw, flags=re.S)
            if match:
                data = json.loads(match.group(0))
                if isinstance(data, dict) and "goal" in data:
                    goal = str(data.get("goal", fallback)).strip()
                    return self._normalize_goal(goal, fallback)
        except Exception:
            logger.debug("JSON substring parsing failed")

        heuristic = re.search(r"goal\s*[:\-]\s*(.+)", raw, flags=re.I)
        if heuristic:
            goal = heuristic.group(1).strip().strip("'\"")
            return self._normalize_goal(goal, fallback)

        excerpt = " ".join(raw.split())[:200]
        logger.info("Using raw excerpt as goal fallback: %s", excerpt)
        return self._normalize_goal(excerpt, fallback)

    def _normalize_goal(self, goal: str, fallback: str) -> str:
        if not goal:
            return fallback
        goal = goal.strip()
        if len(goal) > 240:
            goal = goal[:240].rsplit(" ", 1)[0] + "..."
        return goal
