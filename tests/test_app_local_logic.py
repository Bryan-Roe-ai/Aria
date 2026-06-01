"""Unit tests for app.py local fallback and prompt reading helpers."""

from __future__ import annotations

import builtins
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app


# ---------------------------------------------------------------------------
# ask_local
# ---------------------------------------------------------------------------


def test_ask_local_empty_prompt_raises_value_error():
    with pytest.raises(ValueError):
        app.ask_local("   ")


def test_ask_local_invalid_system_prompt_raises_value_error():
    with pytest.raises(ValueError):
        app.ask_local("hello", system_prompt="   ")


def test_ask_local_summary_branch_for_long_prompt():
    prompt = "This is a sentence about Aria. " * 12

    result = app.ask_local(prompt)

    assert result.startswith("[Local fallback summary]")
    assert "Summary:" in result


def test_ask_local_summary_branch_uses_summary_request_helpers(monkeypatch):
    monkeypatch.setattr(app, "is_summary_request", lambda lower: True)
    monkeypatch.setattr(
        app,
        "summarize_text",
        lambda text, max_sentences, max_chars: "stubbed summary",
    )

    result = app.ask_local("please summarize this short note")

    assert result.startswith("[Local fallback summary]")
    assert "Summary:" in result
    assert "stubbed summary" in result


@pytest.mark.parametrize("prompt", ["explain quantum computing", "what is x"])
def test_ask_local_explanation_branch(prompt):
    result = app.ask_local(prompt)

    assert result.startswith("[Local fallback explanation]")
    assert "Brief explanation:" in result


def test_ask_local_default_branch_echoes_prompt():
    prompt = "hello there friend"

    result = app.ask_local(prompt)

    assert result.startswith("[Local fallback mode]")
    assert "Prompt:" in result
    assert prompt in result


# ---------------------------------------------------------------------------
# _read_prompt
# ---------------------------------------------------------------------------


def test_read_prompt_joins_args():
    assert app._read_prompt(["hello", "world"]) == "hello world"


class _FakePipedStdin:
    def isatty(self) -> bool:
        return False

    def read(self, n: int) -> str:
        return "from stdin\n"


def test_read_prompt_reads_from_non_tty_stdin(monkeypatch):
    monkeypatch.setattr(app.sys, "stdin", _FakePipedStdin())

    assert app._read_prompt([]) == "from stdin"


class _FakeInteractiveStdin:
    def isatty(self) -> bool:
        return True


def test_read_prompt_returns_empty_string_on_eof(monkeypatch):
    monkeypatch.setattr(app.sys, "stdin", _FakeInteractiveStdin())

    def raise_eof(prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr(builtins, "input", raise_eof)

    assert app._read_prompt([]) == ""


def test_read_prompt_reads_interactive_input(monkeypatch):
    monkeypatch.setattr(app.sys, "stdin", _FakeInteractiveStdin())
    monkeypatch.setattr(builtins, "input", lambda prompt: "typed")

    assert app._read_prompt([]) == "typed"
