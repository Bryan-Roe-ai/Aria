"""Unit tests for app.py CLI parsing and provider error fallback behavior."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app

# ---------------------------------------------------------------------------
# _build_parser
# ---------------------------------------------------------------------------


def test_build_parser_defaults():
    args = app._build_parser().parse_args([])

    assert args.prompt == []
    assert args.model == app.DEFAULT_MODEL
    assert args.temperature == app.DEFAULT_TEMPERATURE
    assert args.system == app.SYSTEM_PROMPT
    assert args.provider == "auto"
    assert args.local_fallback is True
    assert args.verbose is False


def test_build_parser_positional_prompt():
    args = app._build_parser().parse_args(["hello", "world"])

    assert args.prompt == ["hello", "world"]


@pytest.mark.parametrize("provider", ["auto", "openai", "quantum", "local"])
def test_build_parser_provider_choices(provider):
    args = app._build_parser().parse_args(["--provider", provider])

    assert args.provider == provider


def test_build_parser_invalid_provider_raises_system_exit():
    with pytest.raises(SystemExit):
        app._build_parser().parse_args(["--provider", "bogus"])


def test_build_parser_no_local_fallback():
    args = app._build_parser().parse_args(["--no-local-fallback"])

    assert args.local_fallback is False


def test_build_parser_temperature_override():
    args = app._build_parser().parse_args(["--temperature", "0.7"])

    assert args.temperature == 0.7


def test_build_parser_model_override():
    args = app._build_parser().parse_args(["--model", "gpt-x"])

    assert args.model == "gpt-x"


def test_build_parser_system_override():
    args = app._build_parser().parse_args(["--system", "be nice"])

    assert args.system == "be nice"


@pytest.mark.parametrize("flag", ["-v", "--verbose"])
def test_build_parser_verbose_flags(flag):
    args = app._build_parser().parse_args([flag])

    assert args.verbose is True


# ---------------------------------------------------------------------------
# _handle_provider_error
# ---------------------------------------------------------------------------


def test_handle_provider_error_uses_local_fallback(capsys):
    result = app._handle_provider_error(
        RuntimeError("boom"),
        "provider failed",
        app.EXIT_API,
        local_fallback=True,
        prompt="hello there",
        system=app.SYSTEM_PROMPT,
    )

    captured = capsys.readouterr()
    assert result == app.EXIT_OK
    assert "[Local fallback" in captured.out
    assert "RuntimeError" in captured.err


def test_handle_provider_error_without_local_fallback(capsys):
    result = app._handle_provider_error(
        RuntimeError("boom"),
        "provider failed",
        app.EXIT_API,
        local_fallback=False,
        prompt="hello there",
        system=app.SYSTEM_PROMPT,
    )

    captured = capsys.readouterr()
    assert result == app.EXIT_API
    assert "provider failed" in captured.err
    assert "boom" in captured.err
    assert "[Local fallback" not in captured.out
