"""
Critique Agent
Evaluates plans or responses against a quality rubric and returns structured
feedback: an overall score, a list of identified issues, and improvement
suggestions.  Useful for self-reflection loops and quality gates in the
autonomous Aria runtime.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from core.agent import BaseAgent
from core.llm.client import LLMClient
from core.memory.store import MemoryStore
from core.task import Task

logger = logging.getLogger(__name__)

_MAX_INPUT_CHARS = 4000
_DEFAULT_SCORE = 0.5


def _clamp_score(value: Any) -> float:
    """Convert *value* to a float clamped to ``[0.0, 1.0]``."""
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return _DEFAULT_SCORE


class CritiqueAgent(BaseAgent):
    """Evaluates content quality and returns a structured critique.

    Accepts tasks of type ``critique``, ``evaluate_response``, or
    ``assess_quality``.  The task payload should contain either a ``response``
    field (the text to evaluate) or a ``plan`` field (a list of plan steps).
    An optional ``criteria`` list can supply custom rubric items; if omitted a
    sensible default rubric is applied.

    Returns a dict with:

    * ``score`` (float 0–1) — overall quality estimate.
    * ``issues`` (list[str]) — detected problems.
    * ``suggestions`` (list[str]) — actionable improvement ideas.
    * ``passed`` (bool) — ``True`` when ``score >= threshold`` (default 0.6).
    """

    name = "critique_agent"

    _DEFAULT_CRITERIA: list[str] = [
        "Is the response accurate and factually correct?",
        "Is it concise and free of unnecessary repetition?",
        "Does it directly address the stated goal?",
        "Are edge cases and potential failure modes acknowledged?",
    ]

    def __init__(
        self,
        memory: MemoryStore,
        llm: LLMClient | None = None,
        threshold: float = 0.6,
    ) -> None:
        self.memory = memory
        self.llm = llm or LLMClient()
        self.threshold = float(threshold)

    def can_handle(self, task: Task) -> bool:
        return task.type in {"critique", "evaluate_response", "assess_quality"}

    def execute(self, task: Task) -> dict[str, Any]:
        payload = task.payload or {}

        content: str = payload.get("response") or payload.get("content") or ""
        plan = payload.get("plan")
        if not content.strip() and isinstance(plan, list):
            content = json.dumps(plan, ensure_ascii=False)

        criteria: list[str] = payload.get("criteria") or self._DEFAULT_CRITERIA

        critique = self._critique(content, criteria)
        critique["agent"] = self.name
        critique["task_id"] = task.id
        critique["passed"] = critique.get("score", 0.0) >= self.threshold

        try:
            self.memory.write("critique_created", critique)
        except Exception:
            logger.exception("Memory write failed when storing critique")

        return critique

    def _critique(self, content: str, criteria: list[str]) -> dict[str, Any]:
        truncated = content[:_MAX_INPUT_CHARS]
        criteria_text = "\n".join(f"- {c}" for c in criteria)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a critique engine. "
                    "Output ONLY a JSON object with these fields: "
                    '"score" (float 0-1), "issues" (list of strings), '
                    '"suggestions" (list of strings).'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Evaluate the following content against these criteria:\n"
                    f"{criteria_text}\n\n"
                    f"Content to evaluate:\n{truncated}"
                ),
            },
        ]

        raw = ""
        try:
            raw = self.llm.complete(messages)
        except Exception:
            logger.exception("LLM client failed during critique")

        return self._parse_critique(raw)

    def _parse_critique(self, raw: str) -> dict[str, Any]:
        fallback: dict[str, Any] = {
            "score": _DEFAULT_SCORE,
            "issues": ["Critique unavailable"],
            "suggestions": [],
        }

        if not raw or not raw.strip():
            return fallback

        def _extract(data: Any) -> dict[str, Any] | None:
            if not isinstance(data, dict):
                return None
            if not any(k in data for k in ("score", "issues", "suggestions")):
                return None
            score = _clamp_score(data.get("score", _DEFAULT_SCORE))
            issues = data.get("issues") or []
            suggestions = data.get("suggestions") or []
            if not isinstance(issues, list):
                issues = [str(issues)]
            if not isinstance(suggestions, list):
                suggestions = [str(suggestions)]
            return {
                "score": score,
                "issues": [str(i) for i in issues],
                "suggestions": [str(s) for s in suggestions],
            }

        try:
            result = _extract(json.loads(raw))
            if result is not None:
                return result
        except Exception:
            pass

        try:
            match = re.search(r"\{.*?\}", raw, re.S)
            if match:
                result = _extract(json.loads(match.group(0)))
                if result is not None:
                    return result
        except Exception:
            pass

        return fallback
