"""Unit tests for chat_cli one-shot stream toggle behavior."""

from __future__ import annotations

import argparse
import importlib.util
import types
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "ai-projects" / "chat-cli" / "src" / "chat_cli.py"


def _load_chat_cli_module():
    spec = importlib.util.spec_from_file_location("chat_cli_for_tests", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_supports_no_stream_flag() -> None:
    module = _load_chat_cli_module()
    parser = module.build_arg_parser()

    args = parser.parse_args(["--once", "hello", "--no-stream"])

    assert args.once == "hello"
    assert args.no_stream is True


def test_one_shot_uses_non_stream_path_when_flag_set(monkeypatch) -> None:
    module = _load_chat_cli_module()

    called = {"non_stream": False, "stream": False}

    class FakeProvider:
        pass

    fake_info = types.SimpleNamespace(name="lmstudio", model="local-model")

    monkeypatch.setattr(
        module,
        "detect_provider",
        lambda explicit, model_override: (FakeProvider(), fake_info),
    )
    monkeypatch.setattr(module, "colorama_init", lambda: None)
    monkeypatch.setattr(module, "print_system", lambda _msg: None)

    def fake_non_stream_reply(_provider, _messages):
        called["non_stream"] = True
        return "OK"

    def fake_stream_reply(_provider, _messages):
        called["stream"] = True
        return "should-not-be-called"

    monkeypatch.setattr(module, "non_stream_assistant_reply", fake_non_stream_reply)
    monkeypatch.setattr(module, "stream_assistant_reply", fake_stream_reply)

    args = argparse.Namespace(
        once="hello",
        system=None,
        provider="lmstudio",
        model=None,
        no_stream=True,
    )

    exit_code = module.one_shot(args)

    assert exit_code == 0
    assert called["non_stream"] is True
    assert called["stream"] is False


def test_one_shot_uses_stream_path_by_default(monkeypatch) -> None:
    module = _load_chat_cli_module()

    called = {"non_stream": False, "stream": False}

    class FakeProvider:
        pass

    fake_info = types.SimpleNamespace(name="lmstudio", model="local-model")

    monkeypatch.setattr(
        module,
        "detect_provider",
        lambda explicit, model_override: (FakeProvider(), fake_info),
    )
    monkeypatch.setattr(module, "colorama_init", lambda: None)
    monkeypatch.setattr(module, "print_system", lambda _msg: None)

    def fake_non_stream_reply(_provider, _messages):
        called["non_stream"] = True
        return "should-not-be-called"

    def fake_stream_reply(_provider, _messages):
        called["stream"] = True
        return "OK"

    monkeypatch.setattr(module, "non_stream_assistant_reply", fake_non_stream_reply)
    monkeypatch.setattr(module, "stream_assistant_reply", fake_stream_reply)

    args = argparse.Namespace(
        once="hello",
        system=None,
        provider="lmstudio",
        model=None,
        no_stream=False,
    )

    exit_code = module.one_shot(args)

    assert exit_code == 0
    assert called["non_stream"] is False
    assert called["stream"] is True


def test_non_stream_reply_handles_api_error_gracefully(monkeypatch) -> None:
    """APIError (e.g. from LM Studio runtime) must not crash — returns error text."""
    module = _load_chat_cli_module()

    class FakeAPIError(Exception):
        pass

    class FakeProvider:
        def complete(self, messages, stream=True):
            raise FakeAPIError("No engine protocol runtime registered")

    captured: dict[str, str] = {}

    monkeypatch.setattr(module, "print_assistant_chunk", lambda t: captured.update({"text": t}))
    monkeypatch.setattr(module, "print_assistant_done", lambda: None)
    monkeypatch.setattr(module, "format_provider_error", lambda e: f"ERR:{e}")

    result = module.non_stream_assistant_reply(FakeProvider(), [{"role": "user", "content": "hi"}])

    assert "ERR:" in result
    assert "ERR:" in captured.get("text", "")
