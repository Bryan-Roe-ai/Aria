"""
Aria Core Runner (Autonomous Runtime)
Transforms Aria into a self-planning, self-improving multi-agent system.
"""

from __future__ import annotations

from typing import Dict, Any
import time

from core.task import Task
from core.registry import AgentRegistry
from core.router import TaskRouter
from core.memory.store import MemoryStore

from core.agents.llm_agent import LLMAgent
from core.agents.tool_agent import ToolAgent
from core.agents.training_agent import TrainingAgent
from core.agents.planner_agent import PlannerAgent
from core.agents.goal_evolution_agent import GoalEvolutionAgent


class AriaRunner:
    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.sleep_seconds = float(self.config.get("sleep_seconds", 2))
        self.max_cycles = self.config.get("max_cycles")

        self.memory = MemoryStore()
        self.registry = AgentRegistry()
        self.router = TaskRouter(self.registry)

        self._setup_agents()

    def _setup_agents(self):
        planner = PlannerAgent(self.memory)
        llm = LLMAgent()
        tool = ToolAgent()
        training = TrainingAgent()
        goal = GoalEvolutionAgent(self.memory)

        tool.registry.register("inspect_context", self._inspect_context)
        tool.registry.register("recent_events", self._recent_events)

        self.registry.register(planner)
        self.registry.register(llm)
        self.registry.register(tool)
        self.registry.register(training)
        self.registry.register(goal)

    def _inspect_context(self, goal: str = "") -> Dict[str, Any]:
        return {
            "goal": goal,
            "event_counts": self.memory.count_by_type(),
            "recent_events": self.memory.last(5),
        }

    def _recent_events(self, limit: int = 5) -> Dict[str, Any]:
        return {"events": self.memory.last(limit)}

    def _run_task(self, task: Task):
        result = self.router.route(task)
        self.memory.write(
            "task_result",
            {
                "task_id": task.id,
                "task_type": task.type,
                "result": result,
            },
        )
        return result

    def _normalize_plan_step(self, step: Any, index: int) -> tuple[Task | None, Dict[str, Any] | None]:
        if not isinstance(step, dict):
            return None, {"index": index, "error": "Plan step must be a dictionary"}

        step_type = step.get("type")
        if not isinstance(step_type, str) or not step_type.strip():
            return None, {"index": index, "error": "Plan step is missing a valid type"}

        payload = step.get("payload", {})
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            return None, {"index": index, "error": "Plan step payload must be a dictionary"}

        try:
            task = Task(
                id=step.get("id"),
                type=step_type,
                payload=payload,
            )
        except Exception as exc:
            return None, {"index": index, "error": str(exc)}
        return task, None

    def _generate_goal(self) -> str:
        """Now delegated to GoalEvolutionAgent via routing."""

        task = Task(
            id="goal_evolve",
            type="goal_evolve",
            payload={}
        )

        result = self.router.route(task)
        return result.get("result", {}).get("goal", "improve system performance")

    def _autonomous_cycle(self):
        goal = self._generate_goal()

        self.memory.write("goal_created", {"goal": goal})

        planner_task = Task(
            id="planner",
            type="plan",
            payload={"goal": goal},
        )

        plan_result = self.router.route(planner_task)
        plan = plan_result.get("result", {}).get("plan", [])
        plan_error = plan_result.get("result", {}).get("error")

        self.memory.write("plan_received", {"plan": plan})

        executed = []
        skipped = []
        for index, step in enumerate(plan):
            task, skip_reason = self._normalize_plan_step(step, index)
            if skip_reason:
                skipped.append(skip_reason)
                self.memory.write("plan_step_skipped", skip_reason)
                continue
            executed.append(self._run_task(task))

        cycle_summary = {
            "goal": goal,
            "plan_length": len(plan),
            "executed_steps": len(executed),
            "skipped_steps": len(skipped),
            "skipped": skipped,
            "plan_error": plan_error,
            "results": executed,
        }
        self.memory.write("cycle_completed", cycle_summary)
        return cycle_summary

    def run_once(self) -> Dict[str, Any]:
        return self._autonomous_cycle()

    def run(self):
        print("[Aria] Autonomous self-improving runtime started.")

        cycle_count = 0
        while True:
            try:
                self._autonomous_cycle()
                cycle_count += 1
                if self.max_cycles is not None and cycle_count >= int(self.max_cycles):
                    break
                time.sleep(self.sleep_seconds)
            except KeyboardInterrupt:
                print("[Aria] Shutdown requested.")
                break
            except Exception as e:
                print("[Aria] Error in cycle:", e)
                time.sleep(self.sleep_seconds)


if __name__ == "__main__":
    AriaRunner().run()
