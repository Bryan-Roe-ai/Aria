"""AGI provider helpers exposed as LM Studio MCP tools."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_agi_factory():
    root = _repo_root()
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    from agi_provider import create_agi_provider

    return create_agi_provider


def _build_messages(query: str | None, messages: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    if isinstance(messages, list) and messages:
        return [
            {"role": str(item.get("role", "user")), "content": str(item.get("content", ""))}
            for item in messages
            if isinstance(item, dict)
        ]
    if isinstance(query, str) and query.strip():
        return [{"role": "user", "content": query.strip()}]
    raise ValueError("Provide either a non-empty query or a messages array")


def _normalize_agi_stream_delta(chunk) -> dict[str, Any]:
    if isinstance(chunk, dict):
        return chunk
    return {"type": "output", "data": str(chunk)}


def _provider_payload(provider, choice) -> dict[str, Any]:
    base = getattr(provider, "_base_provider_choice", None)
    if base is not None:
        base_provider = getattr(base, "name", None)
        base_model = getattr(base, "model", None)
    else:
        base_provider = getattr(choice, "name", None)
        base_model = getattr(choice, "model", None)
    return {
        "name": "agi",
        "base_provider": base_provider,
        "base_model": base_model,
        "wrapper_model": getattr(choice, "model", None),
    }


def run_agi_analyze(query: str) -> dict[str, Any]:
    """Analyze a query with AGI routing metadata."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query is required")

    create_agi_provider = _load_agi_factory()
    provider, choice = create_agi_provider()

    analysis = provider._analyze_query(query.strip())
    selected_agent, agent_score = provider._select_agent(analysis)

    return {
        "success": True,
        "query": query.strip(),
        "analysis": analysis,
        "routing": {
            "selected_agent": selected_agent,
            "agent_score": float(agent_score),
        },
        "provider": _provider_payload(provider, choice),
    }


def run_agi_reason(
    query: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    *,
    include_reasoning_summary: bool = True,
) -> dict[str, Any]:
    """Run full AGI completion and return response payload."""
    chat_messages = _build_messages(query, messages)
    create_agi_provider = _load_agi_factory()
    provider, choice = create_agi_provider()
    result = provider.complete(chat_messages, stream=False)
    if hasattr(result, "__iter__") and not isinstance(result, str):
        result = "".join(str(chunk) for chunk in result)

    payload: dict[str, Any] = {
        "success": True,
        "response": str(result),
        "provider": _provider_payload(provider, choice),
    }
    if include_reasoning_summary:
        payload["reasoning"] = provider.get_reasoning_summary()
    return payload


def run_agi_stream(
    query: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    *,
    include_deltas: bool = True,
) -> dict[str, Any]:
    """Run AGI streaming completion and return structured deltas plus full text."""
    chat_messages = _build_messages(query, messages)
    create_agi_provider = _load_agi_factory()
    provider, choice = create_agi_provider()
    gen = provider.complete(chat_messages, stream=True)

    deltas: list[dict[str, Any]] = []
    text_parts: list[str] = []
    for chunk in gen:
        delta = _normalize_agi_stream_delta(chunk)
        if include_deltas:
            deltas.append(delta)
        if delta.get("type") == "output":
            text_parts.append(str(delta.get("data", "")))

    payload: dict[str, Any] = {
        "success": True,
        "response": "".join(text_parts),
        "provider": _provider_payload(provider, choice),
    }
    if include_deltas:
        payload["deltas"] = deltas
    return payload
