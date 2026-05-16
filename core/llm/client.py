"""
Aria LLM Client
Unified abstraction layer for future model providers (OpenAI, local, Ollama, etc.).
Currently a lightweight offline simulator returning deterministic JSON outputs.
"""

from __future__ import annotations

import json
from typing import Dict, Any, List


class LLMClient:
    def __init__(self, model: str = "auto"):
        self.model = model

    def complete(self, messages: List[Dict[str, str]]) -> str:
        """Return deterministic JSON matching the caller's requested format."""
        system_prompt = ""
        user_prompt = ""
        for message in messages:
            role = message.get("role")
            if role == "system":
                system_prompt = message.get("content", "")
            elif role == "user":
                user_prompt = message.get("content", "")

        return self._simulate(system_prompt=system_prompt, prompt=user_prompt)

    def _simulate(self, *, system_prompt: str, prompt: str) -> str:
        if not prompt.strip():
            return json.dumps({})

        normalized_system = system_prompt.lower()
        if "json list of tasks" in normalized_system:
            goal = self._extract_goal(prompt)
            return json.dumps(self._plan_for_goal(goal))

        if "json object with a single field: goal" in normalized_system:
            return json.dumps({"goal": self._next_goal(prompt)})

        return json.dumps(
            {
                "analysis": f"Processed: {prompt.strip()}",
                "steps": self._infer_steps(prompt),
                "output": f"Simulated result for: {prompt.strip()}",
            }
        )

    def _extract_goal(self, prompt: str) -> str:
        marker = "Goal:"
        if marker in prompt:
            goal_section = prompt.split(marker, 1)[1]
            goal = goal_section.split("Context:", 1)[0].strip()
            if goal:
                return goal
        return prompt.strip()

    def _plan_for_goal(self, goal: str) -> List[Dict[str, Any]]:
        lowered = goal.lower()
        steps: List[Dict[str, Any]] = [
            {"type": "llm", "payload": {"prompt": f"Analyze goal: {goal}"}}
        ]
        if any(token in lowered for token in ("tool", "api", "command", "file")):
            steps.append(
                {
                    "type": "tool",
                    "payload": {
                        "tool": "inspect_context",
                        "args": {"goal": goal},
                    },
                }
            )
        if any(token in lowered for token in ("train", "learn", "improve", "optimize")):
            steps.append(
                {
                    "type": "train",
                    "payload": {"goal": goal, "mode": "record-improvement-signal"},
                }
            )
        if len(steps) == 1:
            steps.append(
                {"type": "llm", "payload": {"prompt": f"Execute next step for: {goal}"}}
            )
        return steps

    def _next_goal(self, prompt: str) -> str:
        lowered = prompt.lower()
        if "plan_created" in lowered or "task_result" in lowered:
            return "review recent execution quality and refine the next plan"
        if "goal_created" in lowered:
            return "turn the current goal into actionable execution steps"
        return "improve system reliability with one measurable next step"

    def _infer_steps(self, prompt: str) -> List[str]:
        lowered = prompt.lower()
        steps = ["understand_goal", "decompose_task", "execute_solution"]
        if any(token in lowered for token in ("verify", "test", "check")):
            steps.append("validate_output")
        return steps
