import json
from pathlib import Path
from types import SimpleNamespace

import function_app


class _FakeReq:
    def __init__(self, method="GET", params=None, body=None, headers=None):
        self.method = method
        self.params = params
        self._body = body
        self.headers = headers or {}

    def get_json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


def test_fallback_validate_request_invalid_json_returns_empty_payload():
    req = _FakeReq(body=ValueError("bad json"))
    payload, err = function_app._fallback_validate_request(req, {})
    assert payload == {}
    assert err is None


def test_serve_text_asset_success(tmp_path: Path):
    f = tmp_path / "asset.txt"
    f.write_text("hello", encoding="utf-8")
    resp = function_app._serve_text_asset(f, mimetype="text/plain", not_found_body="not found")
    assert resp.status_code == 200
    assert resp.get_body().decode("utf-8") == "hello"


def test_serve_text_asset_not_found(tmp_path: Path):
    resp = function_app._serve_text_asset(tmp_path / "missing.txt", mimetype="text/plain", not_found_body="not found")
    assert resp.status_code == 404
    assert resp.get_body().decode("utf-8") == "not found"


def test_health_uses_runtime_provider_detector(monkeypatch):
    def _fake_detect(*, explicit=None, model_override=None, temperature=None, max_output_tokens=None):
        _ = (explicit, model_override, temperature, max_output_tokens)
        return object(), SimpleNamespace(name="local", model="local-echo")

    monkeypatch.setattr(function_app, "_detect_provider_with_runtime_fallback", _fake_detect)
    resp = function_app.health(_FakeReq())
    payload = json.loads(resp.get_body().decode("utf-8"))
    assert resp.status_code == 200
    assert payload["status"] == "ok"
    assert payload["provider"] == "local"


def test_ai_provider_probe_handles_none_params(monkeypatch):
    def _fake_detect(*, explicit=None, model_override=None, temperature=None, max_output_tokens=None):
        _ = (explicit, model_override, temperature, max_output_tokens)
        return object(), SimpleNamespace(name="local", model="local-echo")

    monkeypatch.setattr(function_app, "_detect_provider_with_runtime_fallback", _fake_detect)
    resp = function_app.ai_provider_probe(_FakeReq(method="GET", params=None))
    payload = json.loads(resp.get_body().decode("utf-8"))
    assert resp.status_code == 200
    assert payload["status"] == "ok"
    assert payload["requested_provider"] == "auto"
    assert payload["resolved_provider"] == "local"import json
from pathlib import Path
from types import SimpleNamespace

import function_app


class _FakeReq:
    def __init__(self, method="GET", params=None, body=None, headers=None):
        self.method = method
        self.params = params
        self._body = body
        self.headers = headers or {}

    def get_json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


def test_fallback_validate_request_invalid_json_returns_empty_payload():
    req = _FakeReq(body=ValueError("bad json"))
    payload, err = function_app._fallback_validate_request(req, {})
    assert payload == {}
    assert err is None


def test_serve_text_asset_success(tmp_path: Path):
    f = tmp_path / "asset.txt"
    f.write_text("hello", encoding="utf-8")
    resp = function_app._serve_text_asset(f, mimetype="text/plain", not_found_body="not found")
    assert resp.status_code == 200
    assert resp.get_body().decode("utf-8") == "hello"


def test_serve_text_asset_not_found(tmp_path: Path):
    resp = function_app._serve_text_asset(tmp_path / "missing.txt", mimetype="text/plain", not_found_body="not found")
    assert resp.status_code == 404
    assert resp.get_body().decode("utf-8") == "not found"


def test_health_uses_runtime_provider_detector(monkeypatch):
    def _fake_detect(*, explicit=None, model_override=None, temperature=None, max_output_tokens=None):
        _ = (explicit, model_override, temperature, max_output_tokens)
        return object(), SimpleNamespace(name="local", model="local-echo")

    monkeypatch.setattr(function_app, "_detect_provider_with_runtime_fallback", _fake_detect)
    resp = function_app.health(_FakeReq())
    payload = json.loads(resp.get_body().decode("utf-8"))
    assert resp.status_code == 200
    assert payload["status"] == "ok"
    assert payload["provider"] == "local"


def test_ai_provider_probe_handles_none_params(monkeypatch):
    def _fake_detect(*, explicit=None, model_override=None, temperature=None, max_output_tokens=None):
        _ = (explicit, model_override, temperature, max_output_tokens)
        return object(), SimpleNamespace(name="local", model="local-echo")

    monkeypatch.setattr(function_app, "_detect_provider_with_runtime_fallback", _fake_detect)
    resp = function_app.ai_provider_probe(_FakeReq(method="GET", params=None))
    payload = json.loads(resp.get_body().decode("utf-8"))
    assert resp.status_code == 200
    assert payload["status"] == "ok"
    assert payload["requested_provider"] == "auto"
    assert payload["resolved_provider"] == "local"