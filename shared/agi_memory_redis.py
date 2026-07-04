"""Optional Redis-backed session memory for AGIProvider."""

from __future__ import annotations

import json
import logging
import os
import threading
from collections.abc import MutableMapping, MutableSequence
from typing import Any

_logger = logging.getLogger(__name__)

MAX_HISTORY_SIZE = 50
MAX_GOALS = 5
MAX_REASONING_CHAINS = 10


class _PersistOnWriteDict(MutableMapping[str, Any]):
    def __init__(self, store: RedisAGIMemory, initial: dict[str, Any] | None = None) -> None:
        self._store = store
        self._data: dict[str, Any] = dict(initial or {})

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._store._persist_state()

    def __delitem__(self, key: str) -> None:
        del self._data[key]
        self._store._persist_state()

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class _PersistOnWriteList(MutableSequence[Any]):
    def __init__(self, store: RedisAGIMemory, initial: list[Any] | None = None) -> None:
        self._store = store
        self._data: list[Any] = list(initial or [])

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value) -> None:
        self._data[index] = value
        self._store._persist_state()

    def __delitem__(self, index) -> None:
        del self._data[index]
        self._store._persist_state()

    def __len__(self) -> int:
        return len(self._data)

    def insert(self, index: int, value: Any) -> None:
        self._data.insert(index, value)
        self._store._persist_state()

    def append(self, value: Any) -> None:
        self._data.append(value)
        self._store._persist_state()

    def clear(self) -> None:
        self._data.clear()
        self._store._persist_state()


class RedisAGIMemory:
    """Redis-backed AGI session memory with AGIContext-compatible attributes."""

    def __init__(
        self,
        session_id: str = "default",
        redis_url: str | None = None,
        *,
        client: Any = None,
        max_history: int = MAX_HISTORY_SIZE,
    ) -> None:
        self.max_history = max_history
        self._session_id = session_id or "default"
        self._lock = threading.RLock()

        if client is not None:
            self._client = client
        else:
            try:
                import redis  # type: ignore[import-untyped]
            except ImportError as exc:
                raise RuntimeError("redis package is required for RedisAGIMemory") from exc

            url = redis_url or os.getenv("QAI_AGI_REDIS_URL") or os.getenv("REDIS_URL")
            if not url:
                raise RuntimeError("QAI_AGI_REDIS_URL or REDIS_URL must be set for Redis memory")
            self._client = redis.from_url(url, decode_responses=True)

        raw = self._client.get(self._state_key())
        if raw:
            try:
                state = json.loads(raw)
            except json.JSONDecodeError as exc:
                _logger.warning(
                    "Invalid Redis AGI state JSON for %s: %s",
                    self._state_key(),
                    exc,
                )
                state = {}
        else:
            state = {}
        self.conversation_history: list[dict[str, Any]] = list(state.get("conversation_history", []))
        self.reasoning_chains: list[list[Any]] = list(state.get("reasoning_chains", []))
        self.learned_patterns: _PersistOnWriteDict = _PersistOnWriteDict(self, state.get("learned_patterns", {}))
        self.goals: _PersistOnWriteList = _PersistOnWriteList(self, state.get("goals", []))

    def _state_key(self) -> str:
        return f"agi:{self._session_id}:state"

    def _persist_state(self) -> None:
        with self._lock:
            payload = {
                "conversation_history": self.conversation_history,
                "reasoning_chains": self.reasoning_chains,
                "goals": list(self.goals),
                "learned_patterns": dict(self.learned_patterns),
            }
            self._client.set(self._state_key(), json.dumps(payload, separators=(",", ":"), ensure_ascii=False))

    def add_message(self, message: dict[str, Any]) -> None:
        with self._lock:
            self.conversation_history.append(
                {
                    "role": str(message.get("role", "user"))[:20],
                    "content": str(message.get("content", "")),
                }
            )
            if len(self.conversation_history) > self.max_history:
                system_msgs = [m for m in self.conversation_history if m.get("role") == "system"]
                other_msgs = [m for m in self.conversation_history if m.get("role") != "system"]
                keep_count = max(0, self.max_history - len(system_msgs))
                self.conversation_history = system_msgs + other_msgs[-keep_count:]
            self._persist_state()

    def add_reasoning_chain(self, chain: list[Any]) -> None:
        with self._lock:
            serialized: list[dict[str, Any]] = []
            for step in chain:
                if hasattr(step, "step_type"):
                    serialized.append(
                        {
                            "step_type": getattr(step, "step_type", ""),
                            "content": getattr(step, "content", ""),
                            "confidence": getattr(step, "confidence", 1.0),
                            "metadata": getattr(step, "metadata", {}),
                        }
                    )
                elif isinstance(step, dict):
                    serialized.append(step)
                else:
                    serialized.append({"step_type": "unknown", "content": str(step)})
            self.reasoning_chains.append(serialized)
            if len(self.reasoning_chains) > MAX_REASONING_CHAINS:
                self.reasoning_chains = self.reasoning_chains[-MAX_REASONING_CHAINS:]
            self._persist_state()

    def get_relevant_context(self, query: str) -> str:
        _ = query
        parts: list[str] = []
        recent = self.conversation_history[-6:]
        if recent:
            parts.append("Recent conversation:")
            for msg in recent:
                role = str(msg.get("role", "unknown"))[:20]
                content = str(msg.get("content", ""))[:200]
                parts.append(f"  {role}: {content}")
        if self.goals:
            safe_goals = [str(g)[:50] for g in list(self.goals)[:3]]
            parts.append(f"Active goals: {', '.join(safe_goals)}")
        return "\n".join(parts)


def create_redis_agi_memory(
    session_id: str | None = None,
    redis_url: str | None = None,
    *,
    client: Any = None,
) -> RedisAGIMemory:
    """Factory helper used by ``create_agi_provider`` and tests."""
    sid = session_id or os.getenv("QAI_AGI_SESSION_ID", "default")
    return RedisAGIMemory(session_id=sid, redis_url=redis_url, client=client)
