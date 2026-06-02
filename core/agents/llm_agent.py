"""
LLM Agent
Core reasoning agent for Aria multi-agent runtime.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from core.agent import BaseAgent
from core.llm.client import LLMClient
from core.task import Task


@dataclass
class ReasoningStep:
    name: str
    detail: str


class LLMAgent(BaseAgent):
    name = "llm_agent"

    def __init__(self, model=None):
        self.model = model
        self.client = LLMClient(model=model or "auto")

    def can_handle(self, task: Task) -> bool:
        return task.type in {"llm", "chat", "reason", "generate"}

    def execute(self, task: Task) -> Dict[str, Any]:
        payload = task.payload or {}
        prompt = payload.get("prompt") or payload.get("message") or ""
        system_prompt = (
            payload.get("system_prompt")
            or payload.get("system")
            or ""
        )
        reasoning_mode = bool(payload.get("reasoning_mode"))

        if reasoning_mode:
            response, reasoning_chain = self._run_reasoning_chain(
                prompt,
                system_prompt=system_prompt,
            )
            parsed = self._parse_response(response)
            steps = parsed.get("steps") or [
                step.name for step in reasoning_chain
            ]
            return {
                "output": parsed.get("output", response),
                "analysis": parsed.get("analysis"),
                "steps": steps,
                "raw_output": response,
                "agent": self.name,
                "task_id": task.id,
                "reasoning_chain": [asdict(step) for step in reasoning_chain],
            }

        response = self._run_llm(prompt, system_prompt=system_prompt)
        parsed = self._parse_response(response)

        return {
            "output": parsed.get("output", response),
            "analysis": parsed.get("analysis"),
            "steps": parsed.get("steps", []),
            "raw_output": response,
            "agent": self.name,
            "task_id": task.id,
        }

    def _run_reasoning_chain(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
    ) -> tuple[str, List[ReasoningStep]]:
        if not prompt:
            return (
                "No input provided",
                [
                    ReasoningStep(
                        name="validate_input",
                        detail="Prompt was empty",
                    )
                ],
            )
        reasoning_chain = [
            ReasoningStep(
                name="analyze",
                detail=f"Analyze request: {prompt[:80]}",
            ),
            ReasoningStep(name="plan", detail="Draft a concise response plan"),
            ReasoningStep(
                name="respond",
                detail="Generate the final response",
            ),
        ]
        response = self._run_llm(prompt, system_prompt=system_prompt)
        return response, reasoning_chain

    def _run_llm(self, prompt: str, *, system_prompt: str = "") -> str:
        if not prompt:
            return "No input provided"

        return self.client.complete(
            [
                {
                    "role": "system",
                    "content": system_prompt
                    or "You are a helpful core reasoning agent.",
                },
                {"role": "user", "content": prompt},
            ]
        )

    def _parse_response(self, response: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(response)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return {"output": response, "steps": []}
