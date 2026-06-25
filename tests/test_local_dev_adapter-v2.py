"""Unit tests for local_dev_adapter.py pure helpers.

Covers CLI argument parsing (defaults, env overrides, explicit flags) and the
``_azure_response_parts`` extraction helper that adapts azure.functions
HttpResponse objects for the non-Flask fallback server.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

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


def test_load_env_file_prefers_existing_env_and_loads_dotenv(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "LMSTUDIO_BASE_URL=http://from-dotenv/v1\nLMSTUDIO_MODEL=dotenv-model\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(adapter, "repo_root", tmp_path)
    monkeypatch.setattr(
        adapter,
        "apply_local_settings",
        lambda: os.environ.setdefault("QAI_ENABLE_LOCAL_TTS", "true"),
    )
    monkeypatch.setenv("LMSTUDIO_BASE_URL", "http://from-env/v1")
    monkeypatch.delenv("LMSTUDIO_MODEL", raising=False)
    monkeypatch.delenv("QAI_ENABLE_LOCAL_TTS", raising=False)

    adapter._load_env_file()

    assert os.environ["QAI_ENABLE_LOCAL_TTS"] == "true"
    assert os.environ["LMSTUDIO_BASE_URL"] == "http://from-env/v1"
    assert os.environ["LMSTUDIO_MODEL"] == "dotenv-model"


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
