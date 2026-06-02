from __future__ import annotations

import json
from typing import Any

from core.agents.reflection_agent import ReflectionAgent
from core.memory.store import MemoryStore
from core.task import Task


class StubLLM:
    """Returns a well-formed reflection JSON payload."""

    def complete(self, _messages):
        return json.dumps(
            {
                "lessons": ["Throttle bursty inputs"],
                "patterns": ["Queue pressure recurs under load"],
                "adjustments": ["Add backpressure"],
                "overall": "System needs backpressure under bursty load.",
            }
        )


def test_reflection_agent_can_handle_task_types() -> None:
    agent = ReflectionAgent(MemoryStore(), llm=StubLLM())
    assert agent.can_handle(Task(type="reflect", payload={}))
    assert agent.can_handle(Task(type="retrospect", payload={}))
    assert agent.can_handle(Task(type="meta_learn", payload={}))
    assert not agent.can_handle(Task(type="hypothesize", payload={}))


def test_reflection_agent_returns_empty_without_history() -> None:
    class UnusedLLM:
        def complete(self, _messages):  # pragma: no cover - must not be called
            raise AssertionError("LLM should not run with empty memory")

    unused_llm: Any = UnusedLLM()
    agent = ReflectionAgent(MemoryStore(), llm=unused_llm)
    result = agent.execute(Task(type="reflect", payload={}))

    assert result["overall"] == "No cycle history available for reflection."
    assert result["lessons"] == []
    assert result["patterns"] == []
    assert result["adjustments"] == []
    assert result["agent"] == "reflection_agent"


def test_reflection_agent_formats_cycle_completed_events() -> None:
    captured = {}

    class CapturingLLM:
        def complete(self, _messages):
            captured["messages"] = _messages
            return json.dumps({"lessons": ["l"], "overall": "ok"})

    memory = MemoryStore()
    memory.write(
        "cycle_completed",
        {
            "goal": "stabilise queue",
            "executed_steps": 5,
            "skipped_steps": 1,
            "self_assessment": {"score": 0.8},
        },
    )

    capturing_llm: Any = CapturingLLM()
    agent = ReflectionAgent(memory, llm=capturing_llm)
    result = agent.execute(Task(type="retrospect", payload={"cycle_limit": 3}))

    user_message = captured["messages"][1]["content"]
    assert "goal=stabilise queue" in user_message
    assert "executed=5" in user_message
    assert "skipped=1" in user_message
    assert "score=0.8" in user_message

    # Result persisted as a reflection_completed event.
    stored = memory.query(event_type="reflection_completed")
    assert len(stored) == 1
    assert stored[0]["data"]["overall"] == "ok"


def test_reflection_agent_falls_back_to_general_events() -> None:
    captured = {}

    class CapturingLLM:
        def complete(self, _messages):
            captured["messages"] = _messages
            return json.dumps({"lessons": ["x"], "overall": "ok"})

    memory = MemoryStore()
    # No cycle_completed events -> falls back to memory.last().
    memory.write("note", {"detail": "ran a probe"})

    capturing_llm: Any = CapturingLLM()
    agent = ReflectionAgent(memory, llm=capturing_llm)
    agent.execute(Task(type="meta_learn", payload={}))

    # The LLM ran on a formatted cycle, proving the last() fallback fired
    # instead of the empty-history short-circuit.
    user_message = captured["messages"][1]["content"]
    assert "Cycle 1:" in user_message


def test_reflection_agent_falls_back_when_llm_fails() -> None:
    class FailingLLM:
        def complete(self, _messages):
            raise RuntimeError("backend down")

    memory = MemoryStore()
    memory.write("cycle_completed", {"goal": "g"})

    failing_llm: Any = FailingLLM()
    agent = ReflectionAgent(memory, llm=failing_llm)
    result = agent.execute(Task(type="reflect", payload={}))

    assert result["overall"] == "Could not complete reflection."
    assert result["lessons"] == ["Reflection unavailable"]


def test_reflection_agent_parses_embedded_json_and_coerces_scalars() -> None:
    class ProseLLM:
        def complete(self, _messages):
            # Direct json.loads(raw) fails on the prose; the regex fallback
            # recovers the embedded object. "lessons" is a scalar, exercising
            # the _to_list coercion path.
            return (
                "Here is my reflection: "
                '{"lessons": "single lesson", "patterns": [], '
                '"adjustments": [], "overall": "recovered"}'
            )

    memory = MemoryStore()
    memory.write("cycle_completed", {"goal": "g"})

    prose_llm: Any = ProseLLM()
    agent = ReflectionAgent(memory, llm=prose_llm)
    result = agent.execute(Task(type="reflect", payload={}))

    assert result["overall"] == "recovered"
    assert result["lessons"] == ["single lesson"]
    assert result["patterns"] == []


def test_reflection_agent_tolerates_invalid_cycle_limit() -> None:
    # A non-numeric cycle_limit must not crash execute(); it falls back to the
    # default rather than raising ValueError.
    agent = ReflectionAgent(MemoryStore(), llm=StubLLM())
    result = agent.execute(
        Task(type="reflect", payload={"cycle_limit": "not-a-number"})
    )

    assert result["overall"] == "No cycle history available for reflection."


def test_reflection_agent_formats_non_dict_cycle_data() -> None:
    captured = {}

    class CapturingLLM:
        def complete(self, _messages):
            captured["messages"] = _messages
            return json.dumps({"lessons": ["x"], "overall": "ok"})

    memory = MemoryStore()
    memory.write("cycle_completed", {"goal": "g1"})
    # Force a non-dict data payload to exercise the else branch of
    # _format_cycles (json.dumps of the raw data).
    memory._events[-1]["data"] = ["raw", "list", "data"]

    capturing_llm: Any = CapturingLLM()
    agent = ReflectionAgent(memory, llm=capturing_llm)
    agent.execute(Task(type="reflect", payload={}))

    user_message = captured["messages"][1]["content"]
    assert "raw" in user_message and "list" in user_message
