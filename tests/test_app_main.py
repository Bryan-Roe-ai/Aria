"""Unit tests for the app.main CLI entrypoint."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app


@pytest.fixture(autouse=True)
def clear_provider_env(monkeypatch):
    """Keep provider selection deterministic for every main() test."""
    for name in (
        "QUANTUM_LLM_BASE_URL",
        "FUNCTIONS_BASE_URL",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_ORG",
    ):
        monkeypatch.delenv(name, raising=False)


def test_main_local_provider_success(capsys):
    exit_code = app.main(["--provider", "local", "hello world prompt"])

    captured = capsys.readouterr()
    assert exit_code == app.EXIT_OK
    assert "[Local fallback" in captured.out
    assert captured.err == ""


def test_main_empty_prompt_returns_usage(capsys):
    exit_code = app.main(["--provider", "local", "   "])

    captured = capsys.readouterr()
    assert exit_code == app.EXIT_USAGE
    assert "Invalid input" in captured.err


def test_main_quantum_provider_success(monkeypatch, capsys):
    monkeypatch.setenv("QUANTUM_LLM_BASE_URL", "http://localhost:7071")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(app, "ask_quantum", lambda *args, **kwargs: "quantum answer")

    exit_code = app.main(["--provider", "quantum", "explain something here"])

    captured = capsys.readouterr()
    assert exit_code == app.EXIT_OK
    assert "quantum answer" in captured.out
    assert captured.err == ""


def test_main_auto_provider_falls_back_to_local_without_remote_env(capsys):
    exit_code = app.main(["explain a thing in detail please"])

    captured = capsys.readouterr()
    assert exit_code == app.EXIT_OK
    assert "[Local fallback" in captured.out
    assert captured.err == ""


def test_main_openai_without_api_key_and_no_local_fallback_returns_auth(capsys):
    exit_code = app.main(
        ["--provider", "openai", "--no-local-fallback", "a prompt here"]
    )

    captured = capsys.readouterr()
    assert exit_code == app.EXIT_AUTH
    assert "OPENAI_API_KEY" in captured.err


def test_main_quantum_http_error_without_local_fallback_returns_api(monkeypatch, capsys):
    monkeypatch.setenv("QUANTUM_LLM_BASE_URL", "http://localhost:7071")

    def raise_http_error(*args, **kwargs):
        raise app.urllib_error.HTTPError(
            url="u", code=500, msg="err", hdrs=None, fp=None
        )

    monkeypatch.setattr(app, "ask_quantum", raise_http_error)

    exit_code = app.main(
        ["--provider", "quantum", "--no-local-fallback", "a prompt here"]
    )

    captured = capsys.readouterr()
    assert exit_code == app.EXIT_API
    assert "Quantum API error" in captured.err


def test_main_quantum_http_error_with_local_fallback_returns_ok(monkeypatch, capsys):
    monkeypatch.setenv("QUANTUM_LLM_BASE_URL", "http://localhost:7071")

    def raise_http_error(*args, **kwargs):
        raise app.urllib_error.HTTPError(
            url="u", code=500, msg="err", hdrs=None, fp=None
        )

    monkeypatch.setattr(app, "ask_quantum", raise_http_error)

    exit_code = app.main(["--provider", "quantum", "a prompt here"])

    captured = capsys.readouterr()
    assert exit_code == app.EXIT_OK
    assert "[Local fallback" in captured.out
