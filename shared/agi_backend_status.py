"""Report AGI persistence and memory backend configuration for status endpoints."""

from __future__ import annotations

import os
from typing import Any, Dict


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").lower() in ("1", "true", "yes")


def build_agi_backend_status(provider: Any | None = None) -> Dict[str, Any]:
    """Return a JSON-safe summary of configured AGI backends (no secret values)."""
    sqlite_path = os.getenv("QAI_AGI_PERSIST_DB") or os.getenv(
        "QAI_AGI_PERSIST_SQLITE")
    jsonl_path = os.getenv("QAI_AGI_PERSIST_PATH")
    jsonl_enabled = _env_truthy("QAI_AGI_PERSIST")

    if sqlite_path:
        persist_type = "sqlite"
    elif jsonl_enabled or jsonl_path:
        persist_type = "jsonl"
    else:
        persist_type = "none"

    attached = getattr(provider, "persistence",
                       None) is not None if provider is not None else False

    memory_env = os.getenv("QAI_AGI_MEMORY_BACKEND", "").strip().lower()
    memory_type = "redis" if memory_env == "redis" else "in_process"

    if provider is not None:
        ctx = getattr(provider, "context", None)
        if ctx is not None and "redis" in type(ctx).__name__.lower():
            memory_type = "redis"

    return {
        "persistence": {
            "type": persist_type,
            "attached": attached,
            "enabled": persist_type != "none",
            "sqlite_path": sqlite_path or None,
            "jsonl_path": jsonl_path or None,
            "read_token_configured": bool(os.getenv("QAI_AGI_PERSIST_READ_TOKEN")),
        },
        "memory": {
            "type": memory_type,
            "backend_env": memory_env or None,
            "redis_url_configured": bool(os.getenv("QAI_AGI_REDIS_URL") or os.getenv("REDIS_URL")),
            "session_id": os.getenv("QAI_AGI_SESSION_ID", "default"),
        },
    }
