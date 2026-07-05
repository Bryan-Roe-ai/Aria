"""
Aria Core Runner (Autonomous Runtime)
Transforms Aria into a self-planning, self-improving multi-agent system.
"""

from __future__ import annotations

import time
from typing import Any

from core.agents.critique_agent import CritiqueAgent
from core.agents.debate_agent import DebateAgent
from core.agents.goal_evolution_agent import GoalEvolutionAgent
from core.agents.human_feedback_agent import HumanFeedbackAgent
from core.agents.hypothesis_agent import HypothesisAgent
from core.agents.llm_agent import LLMAgent
from core.agents.planner_agent import PlannerAgent
from core.agents.reasoning_agent import ReasoningAgent
from core.agents.reflection_agent import ReflectionAgent
from core.agents.summarizer_agent import SummarizerAgent
from core.agents.tool_agent import ToolAgent
from core.agents.training_agent import TrainingAgent
from core.bus import AgentBus
from core.cycle_observer import CycleObserver
from core.knowledge.graph import ConceptLinker, KnowledgeGraph
from core.memory.store import MemoryStore
from core.registry import AgentRegistry
from core.router import TaskRouter
from core.task import Task


class AriaRunner:
    """Coordinates autonomous planning, execution, and self-assessment."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.sleep_seconds = self._parse_sleep_seconds(
            self.config.get("sleep_seconds", 2),
        )
        self.max_cycles = self._parse_max_cycles(
            self.config.get("max_cycles"),
        )

        self.memory = MemoryStore(db_path=self.config.get("memory_db_path"))
        self.registry = AgentRegistry()
        self.router = TaskRouter(self.registry)
        self.bus = AgentBus()
        self.knowledge_graph = KnowledgeGraph()
        self.concept_linker = ConceptLinker(self.knowledge_graph, self.memory)
        self.observer = CycleObserver(self.bus, self.memory)

        self._setup_agents()

    @staticmethod
    def _parse_sleep_seconds(value: Any) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 2.0
        return max(0.0, parsed)

    @staticmethod
    def _parse_max_cycles(value: Any) -> int | None:
        if value is None:
            return None
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None
        if parsed <= 0:
            return None
        return parsed

    @staticmethod
    def _parse_target_score(value: Any) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 0.7
        return min(1.0, max(0.0, parsed))

    @staticmethod
    def _normalize_limit(value: Any, default: int = 5) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default
        return max(0, parsed)

    def _setup_agents(self):
        planner = PlannerAgent(self.memory)
        llm = LLMAgent()
        tool = ToolAgent()
        training = TrainingAgent()
        goal = GoalEvolutionAgent(self.memory)
        feedback = HumanFeedbackAgent(self.memory, self.bus)
        summarizer = SummarizerAgent(self.memory)
        critique = CritiqueAgent(self.memory)
        reasoning = ReasoningAgent(self.memory)
        debate = DebateAgent(self.memory)
        hypothesis = HypothesisAgent(self.memory)
        reflection = ReflectionAgent(self.memory)

        tool.registry.register("inspect_context", self._inspect_context)
        tool.registry.register("recent_events", self._recent_events)
        tool.registry.register(
            "knowledge_neighbors",
            self._knowledge_neighbors,
        )
        tool.registry.register("knowledge_related", self._knowledge_related)
        tool.registry.register("knowledge_path", self._knowledge_path)

        self.registry.register(planner)
        self.registry.register(llm)
        self.registry.register(tool)
        self.registry.register(training)
        self.registry.register(goal)
        self.registry.register(feedback)
        self.registry.register(summarizer)
        self.registry.register(critique)
        self.registry.register(reasoning)
        self.registry.register(debate)
        self.registry.register(hypothesis)
        self.registry.register(reflection)

    def _inspect_context(self, goal: str = "") -> dict[str, Any]:
        return {
            "goal": goal,
            "event_counts": self.memory.count_by_type(),
            "recent_events": self.memory.last(5),
        }

    def _recent_events(self, limit: int = 5) -> dict[str, Any]:
        safe_limit = self._normalize_limit(limit, default=5)
        return {"events": self.memory.last(safe_limit)}

    def _knowledge_neighbors(self, entity: str) -> dict[str, Any]:
        return {
            "entity": entity,
            "neighbors": self.knowledge_graph.neighbors(entity),
        }

    def _knowledge_related(
        self,
        entity: str,
        max_depth: int = 2,
    ) -> dict[str, Any]:
        return {
            "entity": entity,
            "related": self.knowledge_graph.find_related(
                entity,
                max_depth=max_depth,
            ),
        }

    def _knowledge_path(self, source: str, target: str) -> dict[str, Any]:
        return {
            "source": source,
            "target": target,
            "path": self.knowledge_graph.shortest_path(source, target),
        }

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

    def _normalize_plan_step(
        self,
        step: Any,
        index: int,
    ) -> tuple[Task | None, dict[str, Any] | None]:
        if not isinstance(step, dict):
            return None, {
                "index": index,
                "error": "Plan step must be a dictionary",
            }

        step_type = step.get("type")
        if not isinstance(step_type, str) or not step_type.strip():
            return None, {
                "index": index,
                "error": "Plan step is missing a valid type",
            }

        payload = step.get("payload", {})
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            return None, {
                "index": index,
                "error": "Plan step payload must be a dictionary",
            }

        try:
            task_id = step.get("id")
            if not isinstance(task_id, str) or not task_id.strip():
                task_id = f"plan-step-{index}"
            task = Task(
                id=task_id,
                type=step_type,
                payload=payload,
                priority=int(step.get("priority", 0)),
            )
        except (TypeError, ValueError) as exc:
            return None, {"index": index, "error": str(exc)}
        return task, None

    def _generate_goal(self) -> str:
        task = Task(id="goal_evolve", type="goal_evolve", payload={})
        result = self.router.route(task)
        return result.get("result", {}).get(
            "goal",
            "improve system performance",
        )

    def _run_self_assess_loop(self, goal: str) -> dict[str, Any] | None:
        training_agent = self.registry.get("training_agent")
        if training_agent is None:
            return None
        assessor = getattr(training_agent, "self_assess", None)
        if not callable(assessor):
            return None

        raw_assessment = assessor(
            target_score=self._parse_target_score(
                self.config.get("target_score", 0.7),
            ),
        )
        if not isinstance(raw_assessment, dict):
            return None

        assessment: dict[str, Any] = dict(raw_assessment)
        assessment_record: dict[str, Any] = {"goal": goal}
        assessment_record.update(assessment)
        self.memory.write(
            "training_self_assessment",
            assessment_record,
        )
        if assessment.get("needs_retraining"):
            retrain_task = Task(
                id="train_self_assess",
                type="train",
                payload={
                    "goal": goal,
                    "source": "self_assess",
                },
            )
            retrain_result = self.router.route(retrain_task)
            assessment["retrain_result"] = retrain_result
        return assessment

    def _extract_plan(
        self,
        plan_result: Any,
    ) -> tuple[list[Any], str | None]:
        if not isinstance(plan_result, dict):
            return [], "Planner returned a non-dictionary response envelope"

        result = plan_result.get("result", {})
        if result is None:
            result = {}
        if not isinstance(result, dict):
            return [], "Planner returned non-dictionary 'result' payload"

        plan = result.get("plan", [])
        if plan is None:
            plan = []
        if not isinstance(plan, list):
            return [], "Planner returned non-list 'plan' payload"

        plan_error = result.get("error")
        if plan_error is None:
            return plan, None
        if isinstance(plan_error, str):
            return plan, plan_error
        return plan, str(plan_error)

    def _autonomous_cycle(self) -> dict[str, Any]:
        with self.observer.cycle() as obs:
            return self._autonomous_cycle_body(obs)
        return {}

    def _autonomous_cycle_body(self, obs: Any) -> dict[str, Any]:
        goal = self._generate_goal()
        self.memory.write("goal_created", {"goal": goal})

        plan_result = self.router.route(
            Task(
                id="planner",
                type="plan",
                payload={"goal": goal},
            ),
        )
        plan, plan_error = self._extract_plan(plan_result)

        self.memory.write(
            "plan_received",
            {
                "plan": plan,
                "plan_error": plan_error,
            },
        )

        executed = []
        skipped = []
        for index, step in enumerate(plan):
            task, skip_reason = self._normalize_plan_step(step, index)
            if skip_reason:
                skipped.append(skip_reason)
                self.memory.write("plan_step_skipped", skip_reason)
                continue
            assert task is not None
            executed.append(self._run_task(task))

        self.concept_linker.link_recent(10)
        assessment = self._run_self_assess_loop(goal)

        failed_steps = sum(
            1
            for routed in executed
            if (isinstance(routed, dict) and isinstance(routed.get("result"), dict) and routed["result"].get("error"))
        )

        cycle_summary: dict[str, Any] = {
            "goal": goal,
            "plan_length": len(plan),
            "executed_steps": len(executed),
            "skipped_steps": len(skipped),
            "failed_steps": failed_steps,
            "skipped": skipped,
            "plan_error": plan_error,
            "results": executed,
        }
        if assessment is not None:
            cycle_summary["self_assessment"] = assessment
        self.memory.write("cycle_completed", cycle_summary)
        obs.set_summary(cycle_summary)
        return cycle_summary

    def run_once(self) -> dict[str, Any]:
        """Run a single autonomous cycle and return its summary."""

        return self._autonomous_cycle()

    def run(self):
        """Run autonomous cycles until stopped or max cycles is reached."""

        print("[Aria] Autonomous self-improving runtime started.")

        cycle_count = 0
        while True:
            try:
                self._autonomous_cycle()
                cycle_count += 1
                if self.max_cycles is not None and cycle_count >= self.max_cycles:
                    break
                time.sleep(self.sleep_seconds)
            except KeyboardInterrupt:
                print("[Aria] Shutdown requested.")
                break
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"[Aria] Error in cycle: {exc!r}")
                time.sleep(self.sleep_seconds)


if __name__ == "__main__":
    AriaRunner().run()
