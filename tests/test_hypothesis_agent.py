from __future__ import annotations

import json
from typing import Any

from core.agents.hypothesis_agent import HypothesisAgent
from core.memory.store import MemoryStore
from core.task import Task


class StubLLM:
    def complete(self, _messages):
        payload = {
            "hypotheses": [
                {
                    "statement": "Bursty inputs create queue pressure",
                    "rationale": (
                        "The observation mentions bursty system behaviour."
                    ),
                    "testable": True,
                }
            ],
            "summary": "Bursty inputs may be driving queue pressure.",
        }
        return (
            "Here is the hypothesis payload:\n"
            f"```json\n{json.dumps(payload, ensure_ascii=False)}\n```"
        )


def test_hypothesis_agent_handles_invalid_limit_and_fenced_json() -> None:
    stub_llm: Any = StubLLM()
    agent = HypothesisAgent(MemoryStore(), llm=stub_llm)
    result = agent.execute(
        Task(
            type="hypothesize",
            payload={
                "observation": {"signal": "burst", "count": 4},
                "limit": "not-a-number",
            },
        )
    )

    assert result["agent"] == "hypothesis_agent"
    assert result["summary"] == "Bursty inputs may be driving queue pressure."
    assert result["hypotheses"][0]["statement"] == (
        "Bursty inputs create queue pressure"
    )
    assert result["hypotheses"][0]["testable"] is True


def test_hypothesis_agent_formats_structured_observations() -> None:
    captured = {}

    class CapturingLLM:
        def complete(self, _messages):
            captured["messages"] = _messages
            return json.dumps(
                {
                    "hypotheses": [
                        {
                            "statement": "ok",
                            "rationale": "ok",
                            "testable": True,
                        }
                    ],
                    "summary": "ok",
                }
            )

    capturing_llm: Any = CapturingLLM()
    agent = HypothesisAgent(MemoryStore(), llm=capturing_llm)
    agent.execute(
        Task(
            type="hypothesize",
            payload={"observation": {"nested": [1, 2, 3]}, "limit": 2},
        )
    )

    user_message = captured["messages"][1]["content"]
    assert '{"nested": [1, 2, 3]}' in user_message
    assert "2–4 testable hypotheses" in user_message


def test_hypothesis_agent_returns_empty_when_no_observations() -> None:
    class UnusedLLM:
        def complete(self, _messages):  # pragma: no cover - must not be called
            raise AssertionError("LLM should not be called with empty memory")

    unused_llm: Any = UnusedLLM()
    agent = HypothesisAgent(MemoryStore(), llm=unused_llm)
    result = agent.execute(Task(type="infer", payload={}))

    assert result["hypotheses"] == []
    assert result["summary"] == (
        "No observations available to hypothesize from."
    )
    assert result["agent"] == "hypothesis_agent"


def test_hypothesis_agent_derives_from_memory_events() -> None:
    captured = {}

    class CapturingLLM:
        def complete(self, _messages):
            captured["messages"] = _messages
            return json.dumps(
                {
                    "hypotheses": [
                        {
                            "statement": "s",
                            "rationale": "r",
                            "testable": False,
                        }
                    ],
                    "summary": "from memory",
                }
            )

    memory = MemoryStore()
    memory.write("error", {"code": 500})
    memory.write("retry", {"attempt": 2})

    capturing_llm: Any = CapturingLLM()
    agent = HypothesisAgent(memory, llm=capturing_llm)
    result = agent.execute(Task(type="generate_hypothesis", payload={}))

    # Memory events were formatted into the prompt instead of an observation.
    user_message = captured["messages"][1]["content"]
    assert 'error: {"code": 500}' in user_message
    assert 'retry: {"attempt": 2}' in user_message
    assert result["summary"] == "from memory"

    # The result is persisted as a hypothesis_generated event.
    stored = memory.query(event_type="hypothesis_generated")
    assert len(stored) == 1
    assert stored[0]["data"]["summary"] == "from memory"


def test_hypothesis_agent_falls_back_when_llm_fails() -> None:
    class FailingLLM:
        def complete(self, _messages):
            raise RuntimeError("backend unavailable")

    failing_llm: Any = FailingLLM()
    agent = HypothesisAgent(MemoryStore(), llm=failing_llm)
    result = agent.execute(
        Task(type="hypothesize", payload={"observation": "something odd"})
    )

    assert result["summary"] == "Could not generate hypotheses."
    assert result["hypotheses"][0]["testable"] is False


def test_hypothesis_agent_falls_back_on_malformed_llm_output() -> None:
    class MalformedLLM:
        def complete(self, _messages):
            return "not valid json at all"

    malformed_llm: Any = MalformedLLM()
    memory = MemoryStore()
    agent = HypothesisAgent(memory, llm=malformed_llm)

    result = agent.execute(
        Task(type="hypothesize", payload={"observation": "something odd"})
    )

    assert result["summary"] == "Could not generate hypotheses."
    assert result["hypotheses"][0]["statement"].startswith(
        "Hypothesis generation failed"
    )
    stored = memory.last_of_type("hypothesis_generated")
    assert stored is not None
    assert stored["data"]["summary"] == "Could not generate hypotheses."


def test_hypothesis_agent_parses_unfenced_json_object() -> None:
    class ProseLLM:
        def complete(self, _messages):
            return (
                "Sure! Here are my thoughts. "
                '{"hypotheses": [{"statement": "x", "rationale": "y", '
                '"testable": true}], "summary": "bare object"} '
                "Let me know if you need more."
            )

    prose_llm: Any = ProseLLM()
    agent = HypothesisAgent(MemoryStore(), llm=prose_llm)
    result = agent.execute(
        Task(type="hypothesize", payload={"observation": "obs"})
    )

    assert result["summary"] == "bare object"
    assert result["hypotheses"][0]["statement"] == "x"
    assert result["hypotheses"][0]["testable"] is True


def test_hypothesis_agent_extracts_object_with_braces_inside_strings() -> None:
    # The hand-rolled brace matcher must ignore '}' and escaped quotes that
    # appear *inside* string values, returning the full outer JSON object.
    tricky_statement = 'He said "done" } now'
    payload = {
        "hypotheses": [
            {
                "statement": tricky_statement,
                "rationale": "embedded brace and quote",
                "testable": True,
            }
        ],
        "summary": "edge } case",
    }

    class TrickyLLM:
        def complete(self, _messages):
            return f"prefix noise {json.dumps(payload)} trailing noise"

    tricky_llm: Any = TrickyLLM()
    agent = HypothesisAgent(MemoryStore(), llm=tricky_llm)
    result = agent.execute(
        Task(type="hypothesize", payload={"observation": "obs"})
    )

    assert result["summary"] == "edge } case"
    assert result["hypotheses"][0]["statement"] == tricky_statement
