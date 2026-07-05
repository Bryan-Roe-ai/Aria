import importlib.util
import os

import pytest


def load_module():
    path = os.path.join(os.path.dirname(__file__), "..", "scripts", "gradio_hello.py")
    path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location("gradio_hello", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load gradio_hello module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_llm_smoke_test_uses_fixed_prompt(monkeypatch):
    m = load_module()
    captured = {}

    def fake_respond(user_message, *args, **kwargs):
        captured["user_message"] = user_message
        yield (
            [{"role": "assistant", "content": "ok"}],
            "",
            [],
            "provider",
            "Complete.",
        )

    monkeypatch.setattr(m, "respond", fake_respond)

    result = m.run_llm_smoke_test(
        [],
        [],
        False,
        "auto",
        None,
        0.7,
        256,
        "English",
        "Aria",
        False,
        10,
        "session",
    )

    assert captured["user_message"] == (
        "LLM smoke test: reply with a short friendly confirmation that the model is working."
    )
    assert result[3] == "provider"
    assert result[4] == "Complete."


def test_llm_smoke_test_returns_last_result(monkeypatch):
    m = load_module()

    def fake_respond(*args, **kwargs):
        yield (
            [{"role": "assistant", "content": "first"}],
            "",
            [],
            "provider",
            "Streaming response...",
        )
        yield (
            [{"role": "assistant", "content": "final"}],
            "",
            [{"user": "x"}],
            "provider",
            "Complete.",
        )

    monkeypatch.setattr(m, "respond", fake_respond)

    result = m.run_llm_smoke_test(
        [],
        [],
        False,
        "auto",
        None,
        0.7,
        256,
        "English",
        "Aria",
        False,
        10,
        "session",
    )

    assert result[0][0]["content"] == "final"
    assert result[2] == [{"user": "x"}]


def test_provider_readiness_note_prefers_lmstudio(monkeypatch):
    m = load_module()
    monkeypatch.setenv("LMSTUDIO_BASE_URL", "http://localhost:1234")

    assert m.provider_readiness_note() == "LM Studio provider ready."


def test_provider_readiness_note_reports_local_fallback_when_unconfigured(monkeypatch):
    m = load_module()
    monkeypatch.delenv("LMSTUDIO_BASE_URL", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_VERSION", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert (
        m.provider_diagnostics_summary()
        == "Provider readiness: No hosted provider configured; local fallback will respond."
    )


def test_provider_status_snapshot_reports_auto_fallback(monkeypatch):
    m = load_module()
    monkeypatch.delenv("LMSTUDIO_BASE_URL", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_VERSION", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert m.provider_status_snapshot("auto") == (
        "auto -> local (local-echo)",
        "No hosted provider configured; local fallback will respond.",
    )


def test_provider_status_snapshot_reports_explicit_local(monkeypatch):
    m = load_module()
    monkeypatch.delenv("LMSTUDIO_BASE_URL", raising=False)

    assert m.provider_status_snapshot("local") == (
        "local (local-echo)",
        "Using local offline fallback.",
    )


def test_reset_chat_session_uses_provider_snapshot(monkeypatch):
    m = load_module()
    monkeypatch.delenv("LMSTUDIO_BASE_URL", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_VERSION", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert m.reset_chat_session("auto") == (
        [],
        [],
        "auto -> local (local-echo)",
        "No hosted provider configured; local fallback will respond.",
    )


def test_reset_chat_session_keeps_explicit_local_status(monkeypatch):
    m = load_module()

    assert m.reset_chat_session("local") == (
        [],
        [],
        "local (local-echo)",
        "Using local offline fallback.",
    )


def test_save_conversation_json_invalid_session_path_raises_chained_value_error(monkeypatch):
    m = load_module()
    monkeypatch.setattr(m, "safe_session_name", lambda *_args, **_kwargs: "../escape")

    with pytest.raises(ValueError, match="Invalid session path") as excinfo:
        m.save_conversation_json([{"user": "hi", "assistant": "hello"}], "ignored")

    assert isinstance(excinfo.value.__cause__, ValueError)
