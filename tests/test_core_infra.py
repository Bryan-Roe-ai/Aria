"""Focused tests for the core infra helpers."""

from __future__ import annotations

import pytest

from core.agents.human_feedback_agent import HumanFeedbackAgent
from core.bus import AgentBus
from core.memory.store import MemoryStore
from core.queue import TaskQueue
from core.task import Task


def test_memory_store_write_query_and_histogram() -> None:
    memory = MemoryStore()
    memory.write("goal_created", {"goal": "ship it"})
    memory.write("goal_created", {"goal": "still shipping"})
    memory.write("plan_created", {"plan": []})

    assert memory.count_by_type()["goal_created"] == 2
    assert len(memory.query(event_type="goal_created")) == 2
    last_plan = memory.last_of_type("plan_created")
    assert last_plan is not None
    assert last_plan["data"]["plan"] == []


def test_agent_bus_publish_returns_isolated_payloads() -> None:
    bus = AgentBus()
    seen_payloads: list[dict] = []

    def first(message: dict) -> dict:
        message["touched"] = True
        seen_payloads.append(message)
        return {"name": "first", "message": message}

    def second(message: dict) -> dict:
        seen_payloads.append(message)
        return {"name": "second", "message": message}

    bus.subscribe("topic", first)
    bus.subscribe("topic", second)

    results = bus.publish("topic", {"value": 1})

    assert results[0]["name"] == "first"
    assert results[1]["name"] == "second"
    assert seen_payloads[0]["touched"] is True
    assert "touched" not in seen_payloads[1]


def test_human_feedback_agent_records_feedback_and_broadcasts() -> None:
    memory = MemoryStore()
    bus = AgentBus()
    published: list[dict] = []

    bus.subscribe(
        "human_feedback",
        lambda message: published.append(message),
    )

    agent = HumanFeedbackAgent(memory, bus)

    result = agent.execute(
        Task(
            type="human_feedback",
            payload={"message": "keep going"},
        )
    )

    assert result["status"] == "recorded"
    assert result["feedback"]["message"] == "keep going"
    assert memory.last_of_type("human_feedback") is not None
    assert published[0]["message"] == "keep going"


@pytest.mark.asyncio
async def test_task_queue_processes_and_stops() -> None:
    queue: TaskQueue = TaskQueue(max_workers=1)
    processed: list[str] = []

    async def handler(task: str) -> None:
        processed.append(task)

    await queue.start(handler)
    await queue.add_task("alpha")
    await queue.stop()

    assert processed == ["alpha"]
    assert queue.pending_count() == 0
