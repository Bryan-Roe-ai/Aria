"""Focused tests for the lightweight core runtime package."""

from __future__ import annotations

from core.agents.tool_agent import ToolAgent
from core.runner import AriaRunner
from core.task import Task


def test_runner_self_assess_loop_records_retrain_result() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0, "target_score": 0.9})
    training_agent = runner.registry.get("training_agent")

    assert training_agent is not None

    routed_tasks: list[Task] = []

    def _self_assess(*, target_score: float = 0.7) -> dict:
        return {
            "target_score": target_score,
            "latest_score": 0.5,
            "history_size": 1,
            "needs_retraining": True,
        }

    def _route(task: Task) -> dict:
        routed_tasks.append(task)
        return {
            "agent": "training_agent",
            "result": {"ack": "training signal recorded"},
        }

    training_agent.self_assess = _self_assess
    runner.router.route = _route

    assessment = runner._run_self_assess_loop("improve reliability")

    assert assessment is not None
    assert assessment["needs_retraining"] is True
    assert assessment["retrain_result"]["agent"] == "training_agent"
    assert routed_tasks[0].type == "train"
    assert routed_tasks[0].payload == {
        "goal": "improve reliability",
        "source": "self_assess",
    }

    memory_event = runner.memory.last_of_type("training_self_assessment")
    assert memory_event is not None
    assert memory_event["data"]["goal"] == "improve reliability"
    assert memory_event["data"]["needs_retraining"] is True


def test_runner_self_assess_loop_skips_retrain_when_not_needed() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0, "target_score": 0.4})
    training_agent = runner.registry.get("training_agent")

    assert training_agent is not None

    routed_tasks: list[Task] = []

    def _self_assess(*, target_score: float = 0.7) -> dict:
        return {
            "target_score": target_score,
            "latest_score": 0.8,
            "history_size": 2,
            "needs_retraining": False,
        }

    def _route(task: Task) -> dict:
        routed_tasks.append(task)
        return {
            "agent": "training_agent",
            "result": {"ack": "training signal recorded"},
        }

    training_agent.self_assess = _self_assess
    runner.router.route = _route

    assessment = runner._run_self_assess_loop("improve throughput")

    assert assessment is not None
    assert assessment["needs_retraining"] is False
    assert "retrain_result" not in assessment
    assert routed_tasks == []

    memory_event = runner.memory.last_of_type("training_self_assessment")
    assert memory_event is not None
    assert memory_event["data"]["goal"] == "improve throughput"
    assert memory_event["data"]["needs_retraining"] is False


def test_runner_normalize_plan_step_falls_back_to_index_id() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0})

    task, skip_reason = runner._normalize_plan_step({"type": "tool", "payload": {"tool": "inspect_context"}}, 3)

    assert skip_reason is None
    assert task is not None
    assert task.id == "plan-step-3"


def test_runner_run_once_executes_cycle_and_records_memory() -> None:
    runner = AriaRunner(config={"max_cycles": 1, "sleep_seconds": 0})

    result = runner.run_once()

    assert result["goal"]
    assert result["plan_length"] >= 1
    assert result["executed_steps"] == len(result["results"])
    assert runner.memory.last_of_type("cycle_completed") is not None


def test_runner_registers_default_tooling() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0})
    tool_agent = runner.registry.get("tool_agent")

    assert tool_agent is not None
    assert isinstance(tool_agent, ToolAgent)
    assert tool_agent.registry.has("inspect_context")
    assert tool_agent.registry.has("recent_events")


def test_runner_default_inspect_context_tool_uses_memory() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0})
    runner.memory.write("goal_created", {"goal": "improve runtime"})
    tool_agent = runner.registry.get("tool_agent")

    assert tool_agent is not None
    result = tool_agent.execute(
        Task(
            type="tool",
            payload={
                "tool": "inspect_context",
                "args": {"goal": "check status"},
            },
        )
    )

    assert result["tool"] == "inspect_context"
    assert result["output"]["goal"] == "check status"
    assert result["output"]["event_counts"]["goal_created"] == 1


def test_runner_knowledge_path_tool_uses_graph_relationships() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0})
    tool_agent = runner.registry.get("tool_agent")

    assert tool_agent is not None

    runner.knowledge_graph.add_relationship("alpha", "beta", "links_to")
    runner.knowledge_graph.add_relationship("beta", "gamma", "links_to")

    result = tool_agent.execute(
        Task(
            type="tool",
            payload={
                "tool": "knowledge_path",
                "args": {"source": "alpha", "target": "gamma"},
            },
        )
    )

    assert result["tool"] == "knowledge_path"
    assert result["output"]["source"] == "alpha"
    assert result["output"]["target"] == "gamma"
    assert result["output"]["path"] == ["alpha", "beta", "gamma"]


def test_runner_skips_invalid_plan_steps_and_records_reason() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0})
    planner = runner.registry.get("planner_agent")

    assert planner is not None

    def _bad_plan(_task: Task) -> dict:
        return {
            "agent": "planner_agent",
            "task_id": "planner",
            "goal": "bad plan",
            "plan": [
                {"payload": {}},
                "oops",
                {"type": "llm", "payload": {"prompt": "ok"}},
            ],
        }

    planner.execute = _bad_plan

    result = runner.run_once()

    assert result["executed_steps"] >= 1
    assert result["skipped_steps"] == 2
    assert runner.memory.last_of_type("plan_step_skipped") is not None


def test_runner_cycle_summary_counts_failed_steps() -> None:
    runner = AriaRunner(config={"sleep_seconds": 0})
    planner = runner.registry.get("planner_agent")
    assert planner is not None

    def _plan_with_failures(_task: Task) -> dict:
        return {
            "agent": "planner_agent",
            "plan": [
                {"type": "tool", "payload": {"tool": "missing", "args": {}}},
                {"type": "llm", "payload": {"prompt": "ok"}},
            ],
        }

    planner.execute = _plan_with_failures

    result = runner.run_once()

    # The "missing" tool step routes to an error result; the llm step succeeds.
    assert result["executed_steps"] == 2
    assert result["failed_steps"] == 1
