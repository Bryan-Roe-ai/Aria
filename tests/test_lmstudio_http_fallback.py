#!/usr/bin/env python3
"""Regression tests for LMStudioProvider HTTP fallback mode.

These tests validate behavior when the optional `openai` SDK is unavailable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).parent.parent
_CHAT_SRC = _REPO_ROOT / "ai-projects" / "chat-cli" / "src"

if str(_CHAT_SRC) not in sys.path:
    sys.path.insert(0, str(_CHAT_SRC))


class _FakeHTTPResponse:
    def __init__(self, body: bytes | None = None, lines: list[bytes] | None = None):
        self._body = body or b""
        self._lines = lines or []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._body

    def __iter__(self):
        return iter(self._lines)


def test_lmstudio_http_fallback_non_stream():
    from chat_providers import LMStudioProvider

    payload = {
        "choices": [
            {
                "message": {
                    "content": "OK",
                }
            }
        ]
    }

    with patch("chat_providers.OpenAI", None):
        provider = LMStudioProvider(base_url="http://127.0.0.1:1234/v1", model="local-model")

    with patch("urllib.request.urlopen", return_value=_FakeHTTPResponse(body=json.dumps(payload).encode("utf-8"))):
        result = provider.complete([{"role": "user", "content": "Reply with OK only."}], stream=False)

    assert result == "OK"


def test_lmstudio_http_fallback_stream():
    from chat_providers import LMStudioProvider

    sse_lines = [
        b'data: {"choices":[{"delta":{"content":"O"}}]}\n',
        b'data: {"choices":[{"delta":{"content":"K"}}]}\n',
        b"data: [DONE]\n",
    ]

    with patch("chat_providers.OpenAI", None):
        provider = LMStudioProvider(base_url="http://127.0.0.1:1234/v1", model="local-model")

    with patch("urllib.request.urlopen", return_value=_FakeHTTPResponse(lines=sse_lines)):
        chunks = provider.complete([{"role": "user", "content": "Reply with OK only."}], stream=True)
        assert not isinstance(chunks, str)
        output = "".join(chunks)

    assert output == "OK"


def test_lmstudio_http_fallback_respects_timeout_env():
    from chat_providers import LMStudioProvider

    captured: dict[str, float] = {}
    payload = {
        "choices": [
            {
                "message": {
                    "content": "OK",
                }
            }
        ]
    }

    def _fake_urlopen(req, timeout=None):
        captured["timeout"] = timeout
        return _FakeHTTPResponse(body=json.dumps(payload).encode("utf-8"))

    with patch("chat_providers.OpenAI", None):
        provider = LMStudioProvider(base_url="http://127.0.0.1:1234/v1", model="local-model")

    with (
        patch.dict("os.environ", {"LMSTUDIO_HTTP_TIMEOUT": "12.5"}, clear=False),
        patch("urllib.request.urlopen", side_effect=_fake_urlopen),
    ):
        result = provider.complete([{"role": "user", "content": "Reply with OK only."}], stream=False)

    assert result == "OK"
    assert captured.get("timeout") == 12.5


def test_lmstudio_no_models_loaded_message():
    from chat_providers import LMStudioProvider

    error_text = "Error code: 400 - {'error': {'message': \"No models loaded. Please load a model in the developer page or use the 'lms load' command.\", 'type': 'invalid_request_error', 'param': 'model', 'code': None}}"

    with patch("chat_providers.OpenAI", None):
        provider = LMStudioProvider(base_url="http://127.0.0.1:1234/v1", model="openai/gpt-oss-20b")

    with patch("urllib.request.urlopen", side_effect=RuntimeError(error_text)):
        result = provider.complete(
            [{"role": "user", "content": "Reply with OK only."}],
            stream=False,
        )

    assert "no model is currently loaded" in result.lower()
    assert "LMSTUDIO_MODEL" in result


def test_lmstudio_timeout_message_is_friendly():
    from chat_providers import LMStudioProvider

    with patch("chat_providers.OpenAI", None):
        provider = LMStudioProvider(base_url="http://127.0.0.1:1234/v1", model="openai/gpt-oss-20b")

    with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
        result = provider.complete(
            [{"role": "user", "content": "Reply with OK only."}],
            stream=False,
        )

    assert "cannot connect to lm studio" in result.lower()
    assert "timed out" in result.lower()
