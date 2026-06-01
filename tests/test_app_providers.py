from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app


class _FakeResp:
    def __init__(self, data: bytes):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._data


def test_ask_quantum_json_response_and_request_payload(monkeypatch):
    captured = {}

    def fake_urlopen(req, *, timeout):
        captured["request"] = req
        captured["timeout"] = timeout
        return _FakeResp(b'{"response": "hi"}')

    monkeypatch.setattr(app.urllib_request, "urlopen", fake_urlopen)

    result = app.ask_quantum(
        " hello ",
        model="test-model",
        temperature=0.4,
        system_prompt=" be precise ",
        base_url="http://x/",
        timeout=12.5,
    )

    assert result == "hi"
    request = captured["request"]
    assert request.full_url == f"http://x{app.QUANTUM_CHAT_PATH}"
    assert request.get_method() == "POST"
    assert captured["timeout"] == 12.5

    payload = json.loads(request.data.decode("utf-8"))
    assert payload == {
        "prompt": "hello",
        "system_prompt": "be precise",
        "messages": [
            {"role": "system", "content": "be precise"},
            {"role": "user", "content": "hello"},
        ],
        "model": "test-model",
        "temperature": 0.4,
    }


def test_ask_quantum_full_url_ends_with_chat_path(monkeypatch):
    captured = {}

    def fake_urlopen(req, *, timeout):
        captured["request"] = req
        return _FakeResp(b'{"response": "ok"}')

    monkeypatch.setattr(app.urllib_request, "urlopen", fake_urlopen)

    assert app.ask_quantum("hi", base_url="http://localhost:7071") == "ok"
    assert captured["request"].full_url.endswith("/api/quantum-llm/chat")


def test_ask_quantum_empty_body_returns_empty(monkeypatch):
    def fake_urlopen(req, *, timeout):
        return _FakeResp(b"")

    monkeypatch.setattr(app.urllib_request, "urlopen", fake_urlopen)

    assert app.ask_quantum("hi") == ""


def test_ask_quantum_non_json_body_returns_raw_text(monkeypatch):
    def fake_urlopen(req, *, timeout):
        return _FakeResp(b"plain")

    monkeypatch.setattr(app.urllib_request, "urlopen", fake_urlopen)

    assert app.ask_quantum("hi") == "plain"


def test_ask_quantum_empty_base_url_raises_before_network(monkeypatch):
    called = False

    def fake_urlopen(req, *, timeout):
        nonlocal called
        called = True
        return _FakeResp(b"{}")

    monkeypatch.setattr(app.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(ValueError, match="Quantum base URL cannot be empty"):
        app.ask_quantum("hi", base_url="  ")
    assert called is False


def test_ask_quantum_invalid_prompt_raises_before_network(monkeypatch):
    called = False

    def fake_urlopen(req, *, timeout):
        nonlocal called
        called = True
        return _FakeResp(b"{}")

    monkeypatch.setattr(app.urllib_request, "urlopen", fake_urlopen)

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        app.ask_quantum("  ")
    assert called is False


def test_ask_ai_calls_responses_api_and_returns_text():
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(output_text="answer")

    client = SimpleNamespace(responses=SimpleNamespace(create=fake_create))

    result = app.ask_ai(
        client,
        " user prompt ",
        model="gpt-test",
        temperature=0.7,
        system_prompt=" system instructions ",
    )

    assert result == "answer"
    assert captured == {
        "model": "gpt-test",
        "input": [
            {"role": "system", "content": "system instructions"},
            {"role": "user", "content": "user prompt"},
        ],
        "temperature": 0.7,
    }


def test_ask_ai_empty_prompt_raises_before_client_called():
    called = False

    def fake_create(**kwargs):
        nonlocal called
        called = True
        return SimpleNamespace(output_text="answer")

    client = SimpleNamespace(responses=SimpleNamespace(create=fake_create))

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        app.ask_ai(client, "  ")
    assert called is False


def test_ask_ai_invalid_temperature_raises_before_client_called():
    called = False

    def fake_create(**kwargs):
        nonlocal called
        called = True
        return SimpleNamespace(output_text="answer")

    client = SimpleNamespace(responses=SimpleNamespace(create=fake_create))

    with pytest.raises(ValueError, match="Temperature must be between"):
        app.ask_ai(client, "hi", temperature=2.1)
    assert called is False
