"""
Smoke tests for AGI endpoints and shared AGI schema.

These are lightweight, fast checks intended to act as a quick gate for AGI-related API surface.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest


def _mock_request(
    method: str = "GET", body: dict | None = None, params: dict | None = None, route_params: dict | None = None
):
    req = MagicMock()
    req.method = method
    req.params = params or {}
    req.route_params = route_params or {}

    if body is not None:
        raw = json.dumps(body).encode("utf-8")
        req.get_json.return_value = body
        req.get_body.return_value = raw
    else:
        req.get_json.side_effect = ValueError("No JSON body")
        req.get_body.return_value = b""

    return req


@pytest.fixture(scope="module")
def app_module():
    """Import function_app once; skip tests if it cannot be imported."""
    try:
        import function_app

        return function_app
    except Exception as exc:
        pytest.skip(f"Cannot import function_app: {exc}")


def test_agi_status_includes_stream_endpoint(app_module):
    req = _mock_request("GET")
    resp = app_module.agi_status(req)
    assert resp.status_code == 200
    data = json.loads(resp.get_body())
    endpoints = data.get("endpoints") or []
    assert any("/api/agi/stream" in e for e in endpoints)


def test_agi_status_exposes_lmstudio_agent_tools(app_module):
    req = _mock_request("GET")
    resp = app_module.agi_status(req)
    assert resp.status_code == 200

    data = json.loads(resp.get_body())
    agent_tools = data.get("agent_tools") or {}
    lmstudio_tools = set(agent_tools.get("lmstudio-specialist") or [])

    assert {
        "list_models",
        "chat_completion",
        "server_status",
    }.issubset(lmstudio_tools)


def test_agi_analyze_requires_query_or_messages(app_module):
    req = _mock_request("POST", body={})
    resp = app_module.agi_analyze(req)
    assert resp.status_code == 400


def test_agi_reason_requires_query_or_messages(app_module):
    req = _mock_request("POST", body={})
    resp = app_module.agi_reason(req)
    assert resp.status_code == 400


def test_agi_stream_requires_query_or_messages(app_module):
    req = _mock_request("POST", body={})
    resp = app_module.agi_stream(req)
    assert resp.status_code == 400


def test_materialize_sse_body_joins_generator_chunks(app_module):
    def _chunks():
        yield b"event: meta\n"
        yield b"data: {}\n\n"

    body = app_module._materialize_sse_body(_chunks())
    assert body == b"event: meta\ndata: {}\n\n"

def test_agi_status_response_schema(app_module):
    """Guard test: ensure agi/status response shape remains stable."""
    req = _mock_request("GET")
    resp = app_module.agi_status(req)
    assert resp.status_code == 200

    data = json.loads(resp.get_body())

    # Required top-level fields
    assert isinstance(data.get("status"), str)
    assert data["status"] in ["ok", "degraded", "error"]
    assert "available" in data
    assert isinstance(data["available"], bool)

    # Provider info
    provider = data.get("provider")
    assert isinstance(provider, dict)
    assert "name" in provider

    # Reasoning summary
    reasoning = data.get("reasoning")
    assert isinstance(reasoning, dict)
    assert "total_reasoning_chains" in reasoning

    # Agent tools metadata
    agent_tools = data.get("agent_tools")
    assert isinstance(agent_tools, dict)
    for agent_name, tools in agent_tools.items():
        assert isinstance(agent_name, str)
        assert isinstance(tools, list)
        assert all(isinstance(t, str) for t in tools)
        assert tools == sorted(tools), f"Tools not sorted for {agent_name}"

    # Endpoints list
    endpoints = data.get("endpoints")
    assert isinstance(endpoints, list)
    assert all(isinstance(e, str) and e.startswith("/") for e in endpoints)


def test_agi_status_agent_tools_deterministic(app_module):
    """Ensure tool metadata output is deterministic across calls."""
    req1 = _mock_request("GET")
    resp1 = app_module.agi_status(req1)
    data1 = json.loads(resp1.get_body())
    tools1 = data1.get("agent_tools") or {}

    req2 = _mock_request("GET")
    resp2 = app_module.agi_status(req2)
    data2 = json.loads(resp2.get_body())
    tools2 = data2.get("agent_tools") or {}

    # Verify consistent structure and content
    assert set(tools1.keys()) == set(tools2.keys())
    for agent_name in tools1:
        assert tools1[agent_name] == tools2[agent_name]
        # Verify no duplicates (set size equals list size)
        assert len(set(tools1[agent_name])) == len(tools1[agent_name])