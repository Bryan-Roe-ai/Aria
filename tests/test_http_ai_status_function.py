from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture(scope="function")
def status_module():
    spec = importlib.util.spec_from_file_location(
        "http_ai_status_module",
        Path(__file__).resolve().parents[1] / "functions" / "http_ai_status" / "__init__.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load functions/http_ai_status/__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MockRequest:
    method = "GET"
    params = {}

    def get_json(self):
        return {}


@pytest.mark.unit
def test_ai_status_includes_local_resolution_runtime_backed(status_module, monkeypatch):
    def fake_detect_provider(explicit="auto", model_override=None):
        if explicit == "local":
            return object(), SimpleNamespace(name="lmstudio", model="phi-3-mini")
        return object(), SimpleNamespace(name="openai", model="gpt-4o-mini")

    monkeypatch.setattr(status_module, "detect_provider", fake_detect_provider)

    resp = status_module.main(MockRequest())
    assert resp.status_code == 200

    body = resp.get_body()
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    data = json.loads(body)

    assert data["active_provider"] == "openai"
    assert "local_resolution" in data
    assert data["local_resolution"]["requested_provider"] == "local"
    assert data["local_resolution"]["resolved_provider"] == "lmstudio"
    assert data["local_resolution"]["resolved_model"] == "phi-3-mini"
    assert data["local_resolution"]["runtime_backed"] is True
    assert data["local_resolution"]["error"] is None


@pytest.mark.unit
def test_ai_status_includes_local_resolution_error(status_module, monkeypatch):
    def fake_detect_provider(explicit="auto", model_override=None):
        if explicit == "local":
            raise RuntimeError("local runtime unavailable")
        return object(), SimpleNamespace(name="local", model="local-echo")

    monkeypatch.setattr(status_module, "detect_provider", fake_detect_provider)

    resp = status_module.main(MockRequest())
    assert resp.status_code == 200

    body = resp.get_body()
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    data = json.loads(body)

    assert data["active_provider"] == "local"
    assert "local_resolution" in data
    assert data["local_resolution"]["requested_provider"] == "local"
    assert data["local_resolution"]["resolved_provider"] is None
    assert data["local_resolution"]["runtime_backed"] is False
    assert "local runtime unavailable" in data["local_resolution"]["error"]
