"""
LLM Agent
Core reasoning agent for Aria multi-agent runtime.
"""

import json
from typing import Dict, Any

from core.agent import BaseAgent
from core.llm.client import LLMClient
from core.task import Task


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
        system_prompt = payload.get("system_prompt") or payload.get("system") or ""

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

    def _run_llm(self, prompt: str, *, system_prompt: str = "") -> str:
        if not prompt:
            return "No input provided"

        return self.client.complete(
            [
                {"role": "system", "content": system_prompt or "You are a helpful core reasoning agent."},
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
