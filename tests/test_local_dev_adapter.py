"""Unit tests for local_dev_adapter.py pure helpers.

Covers CLI argument parsing (defaults, env overrides, explicit flags) and the
``_azure_response_parts`` extraction helper that adapts azure.functions
HttpResponse objects for the non-Flask fallback server.
"""

from __future__ import annotations

import json

import pytest

import local_dev_adapter as adapter


class _FakeResp:
    """Minimal stand-in for azure.functions.HttpResponse."""

    def __init__(self, body, status_code=200, mimetype=None, headers=None):
        self._body = body
        self.status_code = status_code
        self.mimetype = mimetype
        self.headers = headers or {}

    def get_body(self):
        return self._body


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------


def test_parse_args_defaults(monkeypatch):
    monkeypatch.delenv("LOCAL_DEV_ADAPTER_HOST", raising=False)
    monkeypatch.delenv("LOCAL_DEV_ADAPTER_PORT", raising=False)

    args = adapter.parse_args([])

    assert args.host == "0.0.0.0"
    assert args.port == 7071


def test_parse_args_env_overrides(monkeypatch):
    monkeypatch.setenv("LOCAL_DEV_ADAPTER_HOST", "127.0.0.1")
    monkeypatch.setenv("LOCAL_DEV_ADAPTER_PORT", "9090")

    args = adapter.parse_args([])

    assert args.host == "127.0.0.1"
    assert args.port == 9090


def test_parse_args_explicit_flags_override_env(monkeypatch):
    monkeypatch.setenv("LOCAL_DEV_ADAPTER_HOST", "127.0.0.1")
    monkeypatch.setenv("LOCAL_DEV_ADAPTER_PORT", "9090")

    args = adapter.parse_args(["--host", "localhost", "--port", "8123"])

    assert args.host == "localhost"
    assert args.port == 8123


def test_parse_args_invalid_port_raises(monkeypatch):
    monkeypatch.delenv("LOCAL_DEV_ADAPTER_PORT", raising=False)

    with pytest.raises(SystemExit):
        adapter.parse_args(["--port", "not-a-number"])


def test_parse_args_invalid_env_port_raises(monkeypatch):
    # Port comes from int(os.getenv(...)) at default-construction time, so an
    # invalid env value raises ValueError before argparse runs.
    monkeypatch.setenv("LOCAL_DEV_ADAPTER_PORT", "not-a-number")

    with pytest.raises(ValueError):
        adapter.parse_args([])


# ---------------------------------------------------------------------------
# _azure_response_parts
# ---------------------------------------------------------------------------


def test_azure_response_parts_uses_explicit_mimetype():
    resp = _FakeResp(b"hello", status_code=201, mimetype="text/plain")

    body, status, mimetype, headers = adapter._azure_response_parts(resp)

    assert body == b"hello"
    assert status == 201
    assert mimetype == "text/plain"
    assert headers == {}


def test_azure_response_parts_detects_json_when_no_mimetype():
    payload = json.dumps({"ok": True}).encode("utf-8")
    resp = _FakeResp(payload)

    body, status, mimetype, _ = adapter._azure_response_parts(resp)

    assert body == payload
    assert status == 200
    assert mimetype == "application/json"


def test_azure_response_parts_reads_content_type_header():
    resp = _FakeResp(b"<html></html>", headers={"Content-Type": "text/html"})

    _, _, mimetype, headers = adapter._azure_response_parts(resp)

    assert mimetype == "text/html"
    assert headers["Content-Type"] == "text/html"


def test_azure_response_parts_reads_lowercase_content_type_header():
    resp = _FakeResp(b"<html></html>", headers={"content-type": "text/html"})

    _, _, mimetype, _ = adapter._azure_response_parts(resp)

    assert mimetype == "text/html"


def test_azure_response_parts_no_mimetype_for_non_json_body():
    resp = _FakeResp(b"plain text body that is not json")

    _, _, mimetype, _ = adapter._azure_response_parts(resp)

    assert mimetype is None


def test_azure_response_parts_coerces_non_bytes_body():
    resp = _FakeResp("string-body")

    body, _, _, _ = adapter._azure_response_parts(resp)

    assert body == b"string-body"
    assert isinstance(body, bytes)


def test_check_status_endpoints_ok(monkeypatch):
    monkeypatch.setattr(adapter, "get_ai_status_parts", lambda: (b"{}", 200, "application/json", {}))
    monkeypatch.setattr(adapter, "get_agi_status_parts", lambda: (b"{}", 200, "application/json", {}))

    assert adapter.check_status_endpoints() == 0


def test_check_status_endpoints_failure(monkeypatch):
    monkeypatch.setattr(adapter, "get_ai_status_parts", lambda: (b"{}", 500, "application/json", {}))
    monkeypatch.setattr(adapter, "get_agi_status_parts", lambda: (b"{}", 200, "application/json", {}))

    assert adapter.check_status_endpoints() == 1


def test_main_check_flag_exits_without_server(monkeypatch):
    monkeypatch.setattr(adapter, "check_status_endpoints", lambda: 0)

    with pytest.raises(SystemExit) as exc:
        adapter.main(["--check"])

    assert exc.value.code == 0
