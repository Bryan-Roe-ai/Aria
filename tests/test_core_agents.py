"""Tests for the core deliberation agents.

Covers the six previously under-tested agents that wrap an LLM client:
critique, reasoning, reflection, summarizer, debate, and hypothesis. Each is
driven with a stub LLM so both the happy path (valid JSON), the embedded-JSON
extraction path, and the graceful fallback path (LLM error / empty output)
are exercised deterministically.
"""

from __future__ import annotations

import json

from core.agents.critique_agent import CritiqueAgent
from core.agents.debate_agent import DebateAgent
from core.agents.hypothesis_agent import HypothesisAgent
from core.agents.reasoning_agent import ReasoningAgent
from core.agents.reflection_agent import ReflectionAgent
from core.agents.summarizer_agent import SummarizerAgent
from core.memory.store import MemoryStore
from core.task import Task


class _StubLLM:
    """Deterministic stand-in for core.llm.client.LLMClient."""

    def __init__(self, raw: str = "", raise_exc: bool = False):
        self.raw = raw
        self.raise_exc = raise_exc
        self.calls: list = []

    def complete(self, messages):
        self.calls.append(messages)
        if self.raise_exc:
            raise RuntimeError("llm down")
        return self.raw


# --------------------------------------------------------------------------- #
# CritiqueAgent
# --------------------------------------------------------------------------- #
def test_critique_can_handle():
    agent = CritiqueAgent(MemoryStore(), _StubLLM())
    assert agent.can_handle(Task(type="critique"))
    assert agent.can_handle(Task(type="assess_quality"))
    assert not agent.can_handle(Task(type="reason"))


def test_critique_happy_path_passes_and_writes_memory():
    memory = MemoryStore()
    raw = json.dumps({"score": 0.9, "issues": ["minor"], "suggestions": ["tighten"]})
    agent = CritiqueAgent(memory, _StubLLM(raw), threshold=0.6)
    result = agent.execute(Task(type="critique", payload={"response": "text"}))

    assert result["score"] == 0.9
    assert result["passed"] is True
    assert result["issues"] == ["minor"]
    assert result["agent"] == "critique_agent"
    assert memory.last_of_type("critique_created") is not None


def test_critique_uses_plan_when_no_response():
    raw = json.dumps({"score": 0.3, "issues": [], "suggestions": []})
    llm = _StubLLM(raw)
    agent = CritiqueAgent(MemoryStore(), llm, threshold=0.6)
    result = agent.execute(Task(type="critique", payload={"plan": [{"step": 1}]}))
    assert result["passed"] is False
    # The plan was serialized into the prompt content.
    assert "step" in json.dumps(llm.calls[0])


def test_critique_fallback_on_llm_error():
    agent = CritiqueAgent(MemoryStore(), _StubLLM(raise_exc=True))
    result = agent.execute(Task(type="critique", payload={"response": "x"}))
    assert result["score"] == 0.5
    assert result["issues"] == ["Critique unavailable"]
    assert result["passed"] is False


def test_critique_extracts_embedded_json():
    raw = 'noise before {"score": 0.8, "issues": [], "suggestions": []} after'
    agent = CritiqueAgent(MemoryStore(), _StubLLM(raw))
    result = agent.execute(Task(type="critique", payload={"response": "x"}))
    assert result["score"] == 0.8


# --------------------------------------------------------------------------- #
# ReasoningAgent
# --------------------------------------------------------------------------- #
def test_reasoning_can_handle():
    agent = ReasoningAgent(MemoryStore(), _StubLLM())
    assert agent.can_handle(Task(type="reason"))
    assert agent.can_handle(Task(type="chain_of_thought"))
    assert not agent.can_handle(Task(type="critique"))


def test_reasoning_no_question_returns_early():
    memory = MemoryStore()
    agent = ReasoningAgent(memory, _StubLLM())
    result = agent.execute(Task(type="reason", payload={}))
    assert result["steps"] == []
    assert result["conclusion"] == "No question provided."
    assert result["confidence"] == 0.0
    # No memory write on the early-return path.
    assert memory.last_of_type("reasoning_completed") is None


def test_reasoning_happy_path_clamps_confidence_and_writes():
    memory = MemoryStore()
    raw = json.dumps({"steps": ["a", "b"], "conclusion": "done", "confidence": 2.0})
    agent = ReasoningAgent(memory, _StubLLM(raw))
    result = agent.execute(Task(type="reason", payload={"question": "why?"}))
    assert result["steps"] == ["a", "b"]
    assert result["conclusion"] == "done"
    assert result["confidence"] == 1.0
    assert memory.last_of_type("reasoning_completed") is not None


def test_reasoning_fallback_on_empty_output():
    agent = ReasoningAgent(MemoryStore(), _StubLLM(""))
    result = agent.execute(Task(type="reason", payload={"prompt": "q"}))
    assert result["steps"] == ["Reasoning unavailable"]
    assert result["confidence"] == 0.0


# --------------------------------------------------------------------------- #
# ReflectionAgent
# --------------------------------------------------------------------------- #
def test_reflection_can_handle():
    agent = ReflectionAgent(MemoryStore(), _StubLLM())
    assert agent.can_handle(Task(type="reflect"))
    assert agent.can_handle(Task(type="meta_learn"))
    assert not agent.can_handle(Task(type="summarize"))


def test_reflection_without_history_returns_placeholder():
    agent = ReflectionAgent(MemoryStore(), _StubLLM())
    result = agent.execute(Task(type="reflect", payload={}))
    assert result["overall"] == "No cycle history available for reflection."
    assert result["lessons"] == []


def test_reflection_happy_path_uses_cycles_and_writes():
    memory = MemoryStore()
    memory.write(
        "cycle_completed",
        {"goal": "g", "executed_steps": 3, "skipped_steps": 0, "self_assessment": {"score": 0.7}},
    )
    raw = json.dumps(
        {
            "lessons": ["learn"],
            "patterns": ["pattern"],
            "adjustments": ["adjust"],
            "overall": "summary sentence",
        }
    )
    agent = ReflectionAgent(memory, _StubLLM(raw))
    result = agent.execute(Task(type="reflect", payload={"cycle_limit": 5}))
    assert result["lessons"] == ["learn"]
    assert result["overall"] == "summary sentence"
    assert memory.last_of_type("reflection_completed") is not None


def test_reflection_fallback_on_error():
    memory = MemoryStore()
    memory.write("cycle_completed", {"goal": "g"})
    agent = ReflectionAgent(memory, _StubLLM(raise_exc=True))
    result = agent.execute(Task(type="reflect"))
    assert result["lessons"] == ["Reflection unavailable"]


# --------------------------------------------------------------------------- #
# SummarizerAgent
# --------------------------------------------------------------------------- #
def test_summarizer_can_handle():
    agent = SummarizerAgent(MemoryStore(), _StubLLM())
    assert agent.can_handle(Task(type="summarize"))
    assert agent.can_handle(Task(type="condense"))
    assert not agent.can_handle(Task(type="reason"))


def test_summarizer_summarizes_provided_text():
    memory = MemoryStore()
    raw = json.dumps({"summary": "short digest"})
    agent = SummarizerAgent(memory, _StubLLM(raw))
    result = agent.execute(Task(type="summarize", payload={"text": "long content here"}))
    assert result["summary"] == "short digest"
    assert memory.last_of_type("summary_created") is not None


def test_summarizer_no_context():
    agent = SummarizerAgent(MemoryStore(), _StubLLM())
    result = agent.execute(Task(type="summarize", payload={}))
    assert result["summary"] == "No context to summarize."


def test_summarizer_summarizes_memory_events():
    memory = MemoryStore()
    memory.write("note", {"text": "hello"})
    raw = json.dumps({"summary": "from events"})
    agent = SummarizerAgent(memory, _StubLLM(raw))
    result = agent.execute(Task(type="summarize", payload={}))
    assert result["summary"] == "from events"


def test_summarizer_heuristic_parse():
    agent = SummarizerAgent(MemoryStore(), _StubLLM("Summary: the gist of it"))
    result = agent.execute(Task(type="summarize", payload={"text": "x"}))
    assert result["summary"] == "the gist of it"


# --------------------------------------------------------------------------- #
# DebateAgent
# --------------------------------------------------------------------------- #
def test_debate_can_handle():
    agent = DebateAgent(MemoryStore(), _StubLLM())
    assert agent.can_handle(Task(type="debate"))
    assert agent.can_handle(Task(type="stress_test"))
    assert not agent.can_handle(Task(type="reason"))


def test_debate_no_claim_returns_early():
    agent = DebateAgent(MemoryStore(), _StubLLM())
    result = agent.execute(Task(type="debate", payload={}))
    assert result["verdict"] == "No claim provided."
    assert result["counter_arguments"] == []


def test_debate_happy_path_with_steelman():
    memory = MemoryStore()
    raw = json.dumps(
        {
            "counter_arguments": ["c1"],
            "weaknesses": ["w1"],
            "steelman": "best defence",
            "verdict": "weak claim",
        }
    )
    agent = DebateAgent(memory, _StubLLM(raw))
    result = agent.execute(Task(type="debate", payload={"claim": "x is true"}))
    assert result["counter_arguments"] == ["c1"]
    assert result["steelman"] == "best defence"
    assert memory.last_of_type("debate_completed") is not None


def test_debate_without_steelman_blanks_field():
    raw = json.dumps(
        {"counter_arguments": [], "weaknesses": [], "steelman": "ignored", "verdict": "v"}
    )
    agent = DebateAgent(MemoryStore(), _StubLLM(raw))
    result = agent.execute(
        Task(type="debate", payload={"claim": "x", "steelman": False})
    )
    assert result["steelman"] == ""


def test_debate_fallback_on_error():
    agent = DebateAgent(MemoryStore(), _StubLLM(raise_exc=True))
    result = agent.execute(Task(type="debate", payload={"claim": "x"}))
    assert result["counter_arguments"] == ["Debate unavailable"]


# --------------------------------------------------------------------------- #
# HypothesisAgent
# --------------------------------------------------------------------------- #
def test_hypothesis_can_handle():
    agent = HypothesisAgent(MemoryStore(), _StubLLM())
    assert agent.can_handle(Task(type="hypothesize"))
    assert agent.can_handle(Task(type="generate_hypothesis"))
    assert not agent.can_handle(Task(type="reason"))


def test_hypothesis_from_observation():
    memory = MemoryStore()
    raw = json.dumps(
        {
            "hypotheses": [
                {"statement": "s1", "rationale": "r1", "testable": True},
                {"statement": "s2", "rationale": "r2", "testable": False},
            ],
            "summary": "narrative",
        }
    )
    agent = HypothesisAgent(memory, _StubLLM(raw))
    result = agent.execute(
        Task(type="hypothesize", payload={"observation": "things happened"})
    )
    assert len(result["hypotheses"]) == 2
    assert result["hypotheses"][0]["testable"] is True
    assert result["summary"] == "narrative"
    assert memory.last_of_type("hypothesis_generated") is not None


def test_hypothesis_no_observation_no_events():
    agent = HypothesisAgent(MemoryStore(), _StubLLM())
    result = agent.execute(Task(type="hypothesize", payload={}))
    assert result["hypotheses"] == []
    assert "No observations" in result["summary"]


def test_hypothesis_derives_from_memory_events():
    memory = MemoryStore()
    memory.write("error", {"msg": "boom"})
    raw = json.dumps({"hypotheses": [{"statement": "s"}], "summary": "sum"})
    agent = HypothesisAgent(memory, _StubLLM(raw))
    result = agent.execute(Task(type="hypothesize", payload={}))
    assert result["hypotheses"][0]["statement"] == "s"
    assert result["hypotheses"][0]["testable"] is False


def test_hypothesis_fallback_on_empty():
    memory = MemoryStore()
    agent = HypothesisAgent(memory, _StubLLM(""))
    result = agent.execute(
        Task(type="hypothesize", payload={"observation": "obs"})
    )
    assert result["hypotheses"][0]["testable"] is False
    assert result["summary"] == "Could not generate hypotheses."
