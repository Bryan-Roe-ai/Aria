"""Unit tests for LMSTUDIO_AGI_INTEGRATION_IMPL._check_lmstudio_available.

The helper probes a LM Studio server's ``/models`` endpoint and returns a
boolean. These tests mock urllib so no network access is required.
"""

from __future__ import annotations

import importlib.util
from contextlib import contextmanager
from pathlib import Path


def _load_module():
    script_path = Path(__file__).parent.parent / "LMSTUDIO_AGI_INTEGRATION_IMPL.py"
    spec = importlib.util.spec_from_file_location(
        "lmstudio_agi_integration_impl", script_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakeResp:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_check_lmstudio_available_true(monkeypatch):
    mod = _load_module()

    import urllib.request

    captured = {}

    def fake_urlopen(request, timeout=None, *a, **k):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return _FakeResp(200)

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    assert mod._check_lmstudio_available() is True
    # Default base URL probed at the /models endpoint with a 2s timeout.
    assert captured["url"] == "http://127.0.0.1:1234/v1/models"
    assert captured["timeout"] == 2


def test_check_lmstudio_available_respects_env_base_url(monkeypatch):
    mod = _load_module()

    import urllib.request

    captured = {}

    def fake_urlopen(request, timeout=None, *a, **k):
        captured["url"] = request.full_url
        return _FakeResp(200)

    monkeypatch.setenv("LMSTUDIO_BASE_URL", "http://example.test:9999/v1")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    assert mod._check_lmstudio_available() is True
    assert captured["url"] == "http://example.test:9999/v1/models"


def test_check_lmstudio_available_non_200(monkeypatch):
    mod = _load_module()

    import urllib.request

    monkeypatch.setattr(
        urllib.request, "urlopen", lambda *a, **k: _FakeResp(500)
    )

    assert mod._check_lmstudio_available() is False


def test_check_lmstudio_available_connection_error(monkeypatch):
    mod = _load_module()

    import urllib.request

    def boom(*a, **k):
        raise OSError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", boom)

    assert mod._check_lmstudio_available() is False
