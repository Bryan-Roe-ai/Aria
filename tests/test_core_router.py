"""Focused tests for the core task router."""

from __future__ import annotations

from core.agent import BaseAgent
from core.agents.llm_agent import LLMAgent
from core.agents.planner_agent import PlannerAgent
from core.memory.store import MemoryStore
from core.registry import AgentRegistry
from core.router import TaskRouter
from core.runner import AriaRunner
from core.task import Task


class _StaticAgent(BaseAgent):
    """Minimal agent that always handles tasks and returns a fixed result."""

    def __init__(self, name: str, result: dict | None = None) -> None:
        self.name = name
        self._result = result or {"agent": name, "ok": True}

    def can_handle(self, task: Task) -> bool:  # noqa: D401 - test helper
        return True

    def execute(self, task: Task) -> dict:
        return self._result


class _ExplodingExecuteAgent(BaseAgent):
    """Agent that handles tasks but raises during execute()."""

    name = "exploding_execute_agent"

    def can_handle(self, task: Task) -> bool:
        return True

    def execute(self, task: Task) -> dict:
        raise RuntimeError("boom in execute")


class _ExplodingHandleAgent(BaseAgent):
    """Agent whose can_handle() raises during scoring."""

    name = "exploding_handle_agent"

    def can_handle(self, task: Task) -> bool:
        raise RuntimeError("boom in can_handle")

    def execute(self, task: Task) -> dict:  # pragma: no cover - never reached
        return {"agent": self.name}


def test_router_prioritizes_matching_agent_types() -> None:
    memory = MemoryStore()
    registry = AgentRegistry()
    planner = PlannerAgent(memory)
    llm = LLMAgent()
    registry.register(planner)
    registry.register(llm)
    router = TaskRouter(registry)

    result = router.route(
        Task(type="plan", payload={"goal": "Investigate files"})
    )

    assert result["agent"] == "planner_agent"
    assert result["candidates"][0]["agent"] == "planner_agent"


def test_router_classifies_reflection_requests_for_reflection_agent() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0})

    result = runner.router.route_text(
        "Reflect on the last cycle and identify lessons"
    )

    assert result["agent"] == "reflection_agent"


def test_router_isolates_agent_execution_failure() -> None:
    registry = AgentRegistry()
    registry.register(_ExplodingExecuteAgent())
    registry.register(_StaticAgent("backup_agent"))
    router = TaskRouter(registry)

    # All agents score equally (base 1.0), so the first-registered exploding
    # agent wins; its failure must be captured, not raised.
    result = router.route(Task(type="anything", payload={}))

    assert result["agent"] == "exploding_execute_agent"
    assert "score" in result
    assert result["result"]["error"] == "Agent execution failed"
    assert result["result"]["agent"] == "exploding_execute_agent"
    assert result["result"]["exception_type"] == "RuntimeError"
    # The losing candidate is still reported.
    candidate_names = {c["agent"] for c in result["candidates"]}
    assert candidate_names == {"exploding_execute_agent", "backup_agent"}


def test_router_skips_agent_whose_can_handle_raises() -> None:
    registry = AgentRegistry()
    registry.register(_ExplodingHandleAgent())
    registry.register(_StaticAgent("healthy_agent"))
    router = TaskRouter(registry)

    result = router.route(Task(type="anything", payload={}))

    # The exploding agent is skipped during scoring; routing still succeeds.
    assert result["agent"] == "healthy_agent"
    assert result["result"] == {"agent": "healthy_agent", "ok": True}
    assert [c["agent"] for c in result["candidates"]] == ["healthy_agent"]
