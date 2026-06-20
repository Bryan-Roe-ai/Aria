"""Unit tests for AGI MCP helper tools."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).parent.parent
LMSTUDIO_MCP_DIR = REPO_ROOT / "ai-projects" / "lmstudio-mcp"
if str(LMSTUDIO_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(LMSTUDIO_MCP_DIR))

from agi_mcp_tools import run_agi_analyze, run_agi_reason  # noqa: E402


class _FakeAgiProvider:
    def _analyze_query(self, query: str):
        assert query == "design a safer routing layer"
        return {
            "complexity": "complex",
            "intent": "coding",
            "domain": "ai",
            "confidence": 0.9,
        }

    def _select_agent(self, analysis):
        return "code-specialist", 0.87

    def complete(self, messages, stream=False):
        assert stream is False
        return "Reasoned AGI response"

    def get_reasoning_summary(self):
        return {"total_reasoning_chains": 1, "available_agents": ["code-specialist"]}


def test_run_agi_analyze_returns_routing(monkeypatch):
    def fake_factory(**kwargs):
        return _FakeAgiProvider(), SimpleNamespace(name="local", model="local-echo")

    monkeypatch.setattr("agi_mcp_tools._load_agi_factory", lambda: fake_factory)

    payload = run_agi_analyze("design a safer routing layer")

    assert payload["success"] is True
    assert payload["routing"]["selected_agent"] == "code-specialist"
    assert payload["provider"]["name"] == "agi"


def test_run_agi_reason_requires_query_or_messages():
    with pytest.raises(ValueError, match="Provide either"):
        run_agi_reason()


def test_run_agi_reason_with_query(monkeypatch):
    def fake_factory(**kwargs):
        return _FakeAgiProvider(), SimpleNamespace(name="local", model="local-echo")

    monkeypatch.setattr("agi_mcp_tools._load_agi_factory", lambda: fake_factory)

    payload = run_agi_reason(query="hello agi")

    assert payload["success"] is True
    assert payload["response"] == "Reasoned AGI response"
    assert payload["reasoning"]["total_reasoning_chains"] == 1


def test_lmstudio_mcp_server_exports_client_without_exit():
    import importlib.util

    spec_path = LMSTUDIO_MCP_DIR / "lmstudio_mcp_server.py"
    spec = importlib.util.spec_from_file_location("lmstudio_mcp_server_client_export", spec_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "LMStudioClient")
    assert hasattr(module, "get_client")
