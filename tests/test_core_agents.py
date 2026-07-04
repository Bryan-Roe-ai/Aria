"""Focused tests for the core agent package."""

from __future__ import annotations

from collections.abc import Callable

import pytest

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
from core.agents.tool_agent import ToolAgent, ToolRegistry
from core.agents.training_agent import TrainingAgent
from core.bus import AgentBus
from core.memory.store import MemoryStore
from core.task import Task


def _make_llm_agent() -> LLMAgent:
    return LLMAgent()


def _make_planner_agent() -> PlannerAgent:
    return PlannerAgent(MemoryStore())


def _make_goal_evolution_agent() -> GoalEvolutionAgent:
    return GoalEvolutionAgent(MemoryStore())


def _make_summarizer_agent() -> SummarizerAgent:
    return SummarizerAgent(MemoryStore())


def _make_critique_agent() -> CritiqueAgent:
    return CritiqueAgent(MemoryStore())


def _make_reasoning_agent() -> ReasoningAgent:
    return ReasoningAgent(MemoryStore())


def _make_debate_agent() -> DebateAgent:
    return DebateAgent(MemoryStore())


def _make_hypothesis_agent() -> HypothesisAgent:
    return HypothesisAgent(MemoryStore())


def _make_reflection_agent() -> ReflectionAgent:
    return ReflectionAgent(MemoryStore())


def _make_training_agent() -> TrainingAgent:
    return TrainingAgent()


def _make_feedback_recorder(published: list[dict]):
    def _record(message: dict) -> None:
        published.append(message)

    return _record


def _make_echo_tool() -> Callable[[str], str]:
    def _echo(text: str) -> str:
        return f"echo:{text}"

    return _echo


@pytest.mark.parametrize(
    ("agent_factory", "task"),
    [
        (_make_llm_agent, Task(type="llm", payload={"prompt": "hello"})),
        (
            _make_planner_agent,
            Task(type="plan", payload={"goal": "organize work"}),
        ),
        (
            _make_goal_evolution_agent,
            Task(type="goal_evolve", payload={}),
        ),
        (
            _make_summarizer_agent,
            Task(type="summarize", payload={"text": "reduce this"}),
        ),
        (
            _make_critique_agent,
            Task(type="critique", payload={"response": "fine"}),
        ),
        (
            _make_reasoning_agent,
            Task(type="reason", payload={"prompt": "explain"}),
        ),
        (
            _make_debate_agent,
            Task(type="debate", payload={"claim": "test this"}),
        ),
        (
            _make_hypothesis_agent,
            Task(type="hypothesize", payload={"topic": "improvement"}),
        ),
        (
            _make_reflection_agent,
            Task(type="reflect", payload={"prompt": "look back"}),
        ),
        (
            _make_training_agent,
            Task(type="train", payload={"goal": "improve"}),
        ),
    ],
)
def test_core_agents_execute_structured_results(agent_factory, task) -> None:
    agent = agent_factory()

    result = agent.execute(task)

    assert isinstance(result, dict)
    assert result.get("agent")


def test_human_feedback_agent_publishes_feedback_events() -> None:
    memory = MemoryStore()
    bus = AgentBus()
    published: list[dict] = []

    bus.subscribe("human_feedback", _make_feedback_recorder(published))
    agent = HumanFeedbackAgent(memory, bus)

    result = agent.execute(Task(type="feedback", payload={"message": "looks good"}))

    assert result["status"] == "recorded"
    assert result["feedback"]["message"] == "looks good"
    assert memory.last_of_type("human_feedback") is not None
    assert published[0]["message"] == "looks good"


def test_tool_agent_can_run_registered_tool() -> None:
    registry = ToolRegistry()
    registry.register("echo", _make_echo_tool())
    agent = ToolAgent(registry)

    result = agent.execute(Task(type="tool", payload={"tool": "echo", "args": {"text": "hi"}}))

    assert result["tool"] == "echo"
    assert result["output"] == "echo:hi"


def test_llm_agent_reasoning_mode_includes_reasoning_chain() -> None:
    agent = LLMAgent()

    result = agent.execute(
        Task(
            type="reason",
            payload={"prompt": "Explain this", "reasoning_mode": True},
        )
    )

    assert result["reasoning_chain"]
    assert result["reasoning_chain"][0]["name"] == "analyze"


def test_hypothesis_agent_uses_memory_events() -> None:
    memory = MemoryStore()
    memory.write("goal_created", {"goal": "reduce latency"})
    memory.write("task_result", {"output": "inspect_context"})

    class _RecordingLLM:
        def __init__(self) -> None:
            self.messages: list[dict] = []

        def complete(self, _messages):
            self.messages = _messages
            return (
                "```json\n"
                '{"hypotheses":[{"statement":"Latency is tied to goal '
                'clarity","rationale":"The memory events show a specific '
                'goal and a tool output.","testable":true}],'
                '"summary":"Memory events suggest a goal-and-tool '
                'pattern."}'
                "\n```"
            )

    llm = _RecordingLLM()
    agent = HypothesisAgent(memory, llm=llm)  # type: ignore[arg-type]

    result = agent.execute(Task(type="hypothesize", payload={"limit": 2}))

    assert result["agent"] == "hypothesis_agent"
    assert result["hypotheses"][0]["statement"] == ("Latency is tied to goal clarity")
    assert 'goal_created: {"goal": "reduce latency"}' in llm.messages[1]["content"]
    assert memory.last_of_type("hypothesis_generated") is not None


def test_hypothesis_agent_short_circuits_when_memory_is_empty() -> None:
    class _FailingLLM:
        def complete(self, _messages):  # pragma: no cover - defensive
            raise AssertionError("LLM should not be called without observations")

    agent = HypothesisAgent(
        MemoryStore(),
        llm=_FailingLLM(),  # type: ignore[arg-type]
    )

    result = agent.execute(Task(type="hypothesize", payload={"limit": 5}))

    assert result["hypotheses"] == []
    assert result["summary"] == ("No observations available to hypothesize from.")
