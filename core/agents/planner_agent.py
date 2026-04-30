"""
Planner Agent
Generates task plans from goals using memory context and autonomous reasoning.
"""

from typing import Dict, Any, List
from core.agent import BaseAgent
from core.task import Task
from core.memory.store import MemoryStore
import uuid


class PlannerAgent(BaseAgent):
    name = "planner_agent"

    def __init__(self, memory: MemoryStore):
        self.memory = memory

    def can_handle(self, task: Task) -> bool:
        return task.type in {"plan", "goal", "decompose"}

    def execute(self, task: Task) -> Dict[str, Any]:
        payload = task.payload or {}
        goal = payload.get("goal") or payload.get("input") or ""

        history = self.memory.last(10)

        plan = self._create_plan(goal, history)

        self.memory.write("plan_created", {
            "goal": goal,
            "plan": plan,
        })

        return {
            "agent": self.name,
            "task_id": task.id,
            "goal": goal,
            "plan": plan,
        }

    def _create_plan(self, goal: str, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simple deterministic planner (will later be replaced with LLM planning).
        """
        steps = []

        if not goal:
            return [{"error": "No goal provided"}]

        # Basic decomposition logic
        steps.append({
            "id": str(uuid.uuid4()),
            "type": "llm",
            "payload": {"prompt": goal},
        })

        steps.append({
            "id": str(uuid.uuid4()),
            "type": "evaluate",
            "payload": {"source": "llm_output"},
        })

        steps.append({
            "id": str(uuid.uuid4()),
            "type": "optimize",
            "payload": {"strategy": "auto"},
        })

        return steps
