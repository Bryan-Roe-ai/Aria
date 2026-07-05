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

    def __init__(self, params=None):
        self.params = params or {}

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


@pytest.mark.unit
def test_ai_status_payload_uses_short_ttl_cache(status_module, monkeypatch):
    calls = {"detect": 0, "venv": 0}

    def fake_detect_provider(explicit="auto", model_override=None):
        calls["detect"] += 1
        if explicit == "local":
            return object(), SimpleNamespace(name="local", model="local-echo")
        return object(), SimpleNamespace(name="openai", model="gpt-4o-mini")

    def fake_build_venv_info(_repo_root, timeout_seconds=10):
        calls["venv"] += 1
        return {
            "path": "/tmp/.venv/bin/python",
            "exists": False,
            "packages": {"available": {}, "versions": {}},
            "error": None,
        }

    monkeypatch.setattr(status_module, "detect_provider", fake_detect_provider)
    monkeypatch.setattr(status_module, "build_venv_info", fake_build_venv_info)
    monkeypatch.setenv("QAI_STATUS_CACHE_TTL", "60")

    first = status_module.main(MockRequest())
    second = status_module.main(MockRequest())

    assert first.status_code == 200
    assert second.status_code == 200
    # First request computes payload (auto + local detection)
    assert calls["detect"] == 2
    # Second request should be served from cache
    assert calls["venv"] == 1


@pytest.mark.unit
def test_ai_status_refresh_param_bypasses_cache(status_module, monkeypatch):
    calls = {"venv": 0}

    def fake_detect_provider(explicit="auto", model_override=None):
        if explicit == "local":
            return object(), SimpleNamespace(name="local", model="local-echo")
        return object(), SimpleNamespace(name="openai", model="gpt-4o-mini")

    def fake_build_venv_info(_repo_root, timeout_seconds=10):
        calls["venv"] += 1
        return {
            "path": "/tmp/.venv/bin/python",
            "exists": False,
            "packages": {"available": {}, "versions": {}},
            "error": None,
        }

    monkeypatch.setattr(status_module, "detect_provider", fake_detect_provider)
    monkeypatch.setattr(status_module, "build_venv_info", fake_build_venv_info)
    monkeypatch.setenv("QAI_STATUS_CACHE_TTL", "60")

    status_module.main(MockRequest())
    status_module.main(MockRequest(params={"refresh": "1"}))

    assert calls["venv"] == 2


# ---------------------------------------------------------------------------
# _get_status_cache_ttl_seconds
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_status_cache_ttl_returns_default(status_module, monkeypatch):
    monkeypatch.delenv("QAI_STATUS_CACHE_TTL", raising=False)
    ttl = status_module._get_status_cache_ttl_seconds()
    assert ttl == status_module._STATUS_CACHE_DEFAULT_TTL_SECONDS


@pytest.mark.unit
def test_get_status_cache_ttl_env_override(status_module, monkeypatch):
    monkeypatch.setenv("QAI_STATUS_CACHE_TTL", "15.5")
    ttl = status_module._get_status_cache_ttl_seconds()
    assert ttl == 15.5


@pytest.mark.unit
def test_get_status_cache_ttl_clamped_to_zero(status_module, monkeypatch):
    monkeypatch.setenv("QAI_STATUS_CACHE_TTL", "-5")
    ttl = status_module._get_status_cache_ttl_seconds()
    assert ttl == 0.0


@pytest.mark.unit
def test_get_status_cache_ttl_clamped_to_max(status_module, monkeypatch):
    monkeypatch.setenv("QAI_STATUS_CACHE_TTL", "99999")
    ttl = status_module._get_status_cache_ttl_seconds()
    assert ttl == 300.0


@pytest.mark.unit
def test_get_status_cache_ttl_invalid_env_uses_default(status_module, monkeypatch):
    monkeypatch.setenv("QAI_STATUS_CACHE_TTL", "not-a-number")
    ttl = status_module._get_status_cache_ttl_seconds()
    assert ttl == status_module._STATUS_CACHE_DEFAULT_TTL_SECONDS


# ---------------------------------------------------------------------------
# _request_wants_refresh
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "param_value,expected",
    [
        ("1", True),
        ("true", True),
        ("yes", True),
        ("y", True),
        ("on", True),
        ("TRUE", True),
        ("0", False),
        ("false", False),
        ("no", False),
        ("", False),
    ],
)
def test_request_wants_refresh_param_values(status_module, param_value, expected):
    req = MockRequest(params={"refresh": param_value})
    assert status_module._request_wants_refresh(req) is expected


@pytest.mark.unit
def test_request_wants_refresh_no_param(status_module):
    req = MockRequest(params={})
    assert status_module._request_wants_refresh(req) is False


@pytest.mark.unit
def test_request_wants_refresh_none_params(status_module):
    req = MockRequest(params=None)
    assert status_module._request_wants_refresh(req) is False


# ---------------------------------------------------------------------------
# _get_cached_payload_json / _set_cached_payload_json
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_cache_set_get_round_trip(status_module):
    # Reset cache state
    with status_module._STATUS_CACHE_LOCK:
        status_module._STATUS_CACHE.update({"key": None, "cached_at": 0.0, "payload_json": None})

    key = ("test-key", None)
    status_module._set_cached_payload_json(key, '{"status":"ok"}')
    result = status_module._get_cached_payload_json(key, ttl_seconds=60.0)
    assert result == '{"status":"ok"}'


@pytest.mark.unit
def test_cache_miss_wrong_key(status_module):
    with status_module._STATUS_CACHE_LOCK:
        status_module._STATUS_CACHE.update({"key": ("k1",), "cached_at": 0.0, "payload_json": '{"x":1}'})
    result = status_module._get_cached_payload_json(("k2",), ttl_seconds=60.0)
    assert result is None


@pytest.mark.unit
def test_cache_ttl_zero_disables_get(status_module):
    key = ("some-key",)
    status_module._set_cached_payload_json(key, '{"ok":1}')
    result = status_module._get_cached_payload_json(key, ttl_seconds=0.0)
    assert result is None


@pytest.mark.unit
def test_cache_expired_entry_returns_none(status_module):
    import time as _time

    key = ("expire-key",)
    with status_module._STATUS_CACHE_LOCK:
        status_module._STATUS_CACHE.update(
            {
                "key": key,
                "cached_at": _time.time() - 100.0,
                "payload_json": '{"old":1}',
            }
        )
    result = status_module._get_cached_payload_json(key, ttl_seconds=1.0)
    assert result is None


@pytest.mark.unit
def test_cache_not_returned_when_payload_not_str(status_module):
    key = ("bad-payload",)
    with status_module._STATUS_CACHE_LOCK:
        import time as _time

        status_module._STATUS_CACHE.update(
            {
                "key": key,
                "cached_at": _time.time(),
                "payload_json": 12345,  # not a string
            }
        )
    result = status_module._get_cached_payload_json(key, ttl_seconds=60.0)
    assert result is None


# ---------------------------------------------------------------------------
# TTL=0 causes cache to be bypassed on main()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_ai_status_ttl_zero_always_computes(status_module, monkeypatch):
    calls = {"venv": 0}

    def fake_detect_provider(explicit="auto", model_override=None):
        if explicit == "local":
            return object(), SimpleNamespace(name="local", model="m")
        return object(), SimpleNamespace(name="local", model="m")

    def fake_build_venv_info(_repo_root, timeout_seconds=10):
        calls["venv"] += 1
        return {"path": "/tmp/.venv", "exists": False, "packages": {"available": {}, "versions": {}}, "error": None}

    monkeypatch.setattr(status_module, "detect_provider", fake_detect_provider)
    monkeypatch.setattr(status_module, "build_venv_info", fake_build_venv_info)
    monkeypatch.setenv("QAI_STATUS_CACHE_TTL", "0")

    status_module.main(MockRequest())
    status_module.main(MockRequest())

    assert calls["venv"] == 2  # never cached
