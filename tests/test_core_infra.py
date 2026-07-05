"""Focused tests for the core infra helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

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


def test_memory_store_zero_capacity_discards_events() -> None:
    memory = MemoryStore(max_events=0)

    memory.write("goal_created", {"goal": "ship it"})

    assert len(memory) == 0
    assert memory.to_list() == []
    assert memory.last_of_type("goal_created") is None


def test_memory_store_treats_naive_datetimes_as_utc() -> None:
    memory = MemoryStore()
    naive_timestamp = datetime(2026, 7, 5, 12, 0, 0)

    event_id = memory.write(
        "goal_created",
        {"goal": "ship it"},
        naive_timestamp,
    )
    stored = memory.get(event_id)
    expected_epoch = naive_timestamp.replace(tzinfo=timezone.utc).timestamp()

    assert stored is not None
    assert stored["timestamp"].endswith("+00:00")
    assert stored["epoch"] == expected_epoch
    assert memory.query(since=naive_timestamp)[0]["id"] == event_id


def test_memory_store_normalizes_aware_datetimes_to_utc() -> None:
    memory = MemoryStore()
    eastern = timezone(timedelta(hours=-5))
    aware_timestamp = datetime(2026, 7, 5, 12, 0, 0, tzinfo=eastern)

    event_id = memory.write(
        "goal_created",
        {"goal": "normalize offset"},
        aware_timestamp,
    )
    stored = memory.get(event_id)
    expected_epoch = aware_timestamp.astimezone(timezone.utc).timestamp()

    assert stored is not None
    assert stored["timestamp"].endswith("+00:00")
    assert stored["epoch"] == expected_epoch
    assert memory.query(since=aware_timestamp)[0]["id"] == event_id


def test_memory_store_until_filter_is_inclusive_for_aware_datetime() -> None:
    memory = MemoryStore()
    eastern = timezone(timedelta(hours=-5))
    event_time = datetime(2026, 7, 5, 12, 0, 0, tzinfo=eastern)

    kept_id = memory.write("goal_created", {"goal": "kept"}, event_time)
    memory.write(
        "goal_created",
        {"goal": "excluded"},
        event_time + timedelta(seconds=1),
    )

    result = memory.query(until=event_time)

    assert [event["id"] for event in result] == [kept_id]


def test_memory_store_since_until_window_for_aware_datetime() -> None:
    memory = MemoryStore()
    eastern = timezone(timedelta(hours=-5))
    start = datetime(2026, 7, 5, 12, 0, 0, tzinfo=eastern)

    memory.write(
        "goal_created",
        {"goal": "before"},
        start - timedelta(seconds=1),
    )
    first_kept = memory.write("goal_created", {"goal": "first_kept"}, start)
    second_kept = memory.write(
        "goal_created",
        {"goal": "second_kept"},
        start + timedelta(seconds=1),
    )
    memory.write(
        "goal_created",
        {"goal": "after"},
        start + timedelta(seconds=2),
    )

    window = memory.query(since=start, until=start + timedelta(seconds=1))

    assert [event["id"] for event in window] == [first_kept, second_kept]


def test_memory_store_window_reverse_order_for_aware_datetime() -> None:
    memory = MemoryStore()
    eastern = timezone(timedelta(hours=-5))
    start = datetime(2026, 7, 5, 12, 0, 0, tzinfo=eastern)

    first_kept = memory.write("goal_created", {"goal": "first_kept"}, start)
    second_kept = memory.write(
        "goal_created",
        {"goal": "second_kept"},
        start + timedelta(seconds=1),
    )

    window = memory.query(
        since=start,
        until=start + timedelta(seconds=1),
        reverse=True,
    )

    assert [event["id"] for event in window] == [second_kept, first_kept]


def test_memory_store_query_type_reverse_limit_combination() -> None:
    memory = MemoryStore()
    memory.write("plan_created", {"plan": [1]})
    first_goal = memory.write("goal_created", {"goal": "first"})
    second_goal = memory.write("goal_created", {"goal": "second"})
    memory.write("plan_created", {"plan": [2]})

    result = memory.query(
        event_type="goal_created",
        reverse=True,
        limit=1,
    )

    assert [event["id"] for event in result] == [second_goal]
    assert result[0]["data"]["goal"] == "second"
    assert first_goal != second_goal


def test_memory_store_rejects_negative_capacity() -> None:
    with pytest.raises(ValueError, match="max_events must be >= 0 or None"):
        MemoryStore(max_events=-1)


def test_memory_store_query_non_positive_limit_returns_empty() -> None:
    memory = MemoryStore()
    memory.write("goal_created", {"goal": "ship it"})

    assert memory.query(limit=0) == []
    assert memory.query(limit=-1) == []


def test_memory_store_query_since_later_than_until_returns_empty() -> None:
    memory = MemoryStore()
    eastern = timezone(timedelta(hours=-5))
    start = datetime(2026, 7, 5, 12, 0, 0, tzinfo=eastern)
    memory.write("goal_created", {"goal": "ship it"}, start)

    assert (
        memory.query(
            since=start + timedelta(seconds=2),
            until=start + timedelta(seconds=1),
        )
        == []
    )


def test_memory_store_query_skips_malformed_epoch_event() -> None:
    memory = MemoryStore()
    valid_id = memory.write("goal_created", {"goal": "valid"})
    memory._events.append(
        {
            "id": "bad-epoch",
            "timestamp": "not-a-real-ts",
            "epoch": "not-a-number",
            "type": "goal_created",
            "data": {"goal": "bad"},
        }
    )

    result = memory.query(event_type="goal_created")

    assert [event["id"] for event in result] == [valid_id]


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
