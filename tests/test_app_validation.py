"""Unit tests for app.py pure validation and extraction helpers.

These cover the input-validation surface (timeout, temperature, prompt, system
prompt, model name), the env helper, stdin reader, and the response/quantum
text extraction logic. They complement test_app_local_fallback.py which
exercises the CLI end-to-end.
"""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app

# ---------------------------------------------------------------------------
# _parse_timeout
# ---------------------------------------------------------------------------


def test_parse_timeout_valid():
    assert app._parse_timeout("12.5") == 12.5


@pytest.mark.parametrize("value", ["abc", "", "nan", "inf", "0", "-3"])
def test_parse_timeout_invalid(value):
    with pytest.raises(ValueError):
        app._parse_timeout(value)


# ---------------------------------------------------------------------------
# _validate_temperature
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0.0, 1.0, 2.0])
def test_validate_temperature_valid(value):
    assert app._validate_temperature(value) == value


@pytest.mark.parametrize("value", [-0.1, 2.1, float("nan"), float("inf")])
def test_validate_temperature_invalid(value):
    with pytest.raises(ValueError):
        app._validate_temperature(value)


# ---------------------------------------------------------------------------
# _validate_prompt
# ---------------------------------------------------------------------------


def test_validate_prompt_strips_and_returns():
    assert app._validate_prompt("  hello  ") == "hello"


def test_validate_prompt_empty_raises():
    with pytest.raises(ValueError):
        app._validate_prompt("   ")


def test_validate_prompt_too_long_raises():
    with pytest.raises(ValueError):
        app._validate_prompt("x" * (app.MAX_PROMPT_CHARS + 1))


def test_validate_prompt_respects_custom_max():
    with pytest.raises(ValueError):
        app._validate_prompt("abcdef", max_chars=3)


# ---------------------------------------------------------------------------
# _validate_system_prompt
# ---------------------------------------------------------------------------


def test_validate_system_prompt_valid():
    assert app._validate_system_prompt("  be helpful ") == "be helpful"


def test_validate_system_prompt_empty_raises():
    with pytest.raises(ValueError):
        app._validate_system_prompt("")


def test_validate_system_prompt_too_long_raises():
    with pytest.raises(ValueError):
        app._validate_system_prompt("x" * (app.MAX_SYSTEM_PROMPT_CHARS + 1))


# ---------------------------------------------------------------------------
# _validate_model_name
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["gpt-4o-mini", "model_1.2:beta", "A.B-C_d:1"])
def test_validate_model_name_valid(name):
    assert app._validate_model_name(name) == name


def test_validate_model_name_empty_raises():
    with pytest.raises(ValueError):
        app._validate_model_name("  ")


def test_validate_model_name_bad_chars_raises():
    with pytest.raises(ValueError):
        app._validate_model_name("bad model!")


def test_validate_model_name_too_long_raises():
    with pytest.raises(ValueError):
        app._validate_model_name("a" * (app.MAX_MODEL_NAME_CHARS + 1))


# ---------------------------------------------------------------------------
# _env_str
# ---------------------------------------------------------------------------


def test_env_str_present(monkeypatch):
    monkeypatch.setenv("APP_TEST_VAR", "  value  ")
    assert app._env_str("APP_TEST_VAR") == "value"


def test_env_str_absent(monkeypatch):
    monkeypatch.delenv("APP_TEST_MISSING", raising=False)
    assert app._env_str("APP_TEST_MISSING") == ""


# ---------------------------------------------------------------------------
# _read_stdin_limited
# ---------------------------------------------------------------------------


def test_read_stdin_limited_reads_one_over_max(monkeypatch):
    import io

    monkeypatch.setattr(app.sys, "stdin", io.StringIO("abcdefghij"))
    # Implementation reads max_chars + 1 so callers can detect overflow.
    assert app._read_stdin_limited(4) == "abcde"


# ---------------------------------------------------------------------------
# _extract_text
# ---------------------------------------------------------------------------


def test_extract_text_prefers_output_text():
    resp = SimpleNamespace(output_text="  direct answer  ", output=None)
    assert app._extract_text(resp) == "direct answer"


def test_extract_text_falls_back_to_output_content():
    text_obj = SimpleNamespace(value="nested value")
    content = SimpleNamespace(type="output_text", text=text_obj)
    item = SimpleNamespace(content=[content])
    resp = SimpleNamespace(output_text=None, output=[item])
    assert app._extract_text(resp) == "nested value"


def test_extract_text_skips_non_text_content():
    content = SimpleNamespace(type="image", text="ignored")
    item = SimpleNamespace(content=[content])
    resp = SimpleNamespace(output_text="", output=[item])
    assert app._extract_text(resp) == ""


def test_extract_text_handles_plain_string_text():
    content = SimpleNamespace(type="text", text="plain string")
    item = SimpleNamespace(content=[content])
    resp = SimpleNamespace(output_text=None, output=[item])
    assert app._extract_text(resp) == "plain string"


# ---------------------------------------------------------------------------
# _extract_quantum_text
# ---------------------------------------------------------------------------


def test_extract_quantum_text_from_string():
    assert app._extract_quantum_text("  hi  ") == "hi"


def test_extract_quantum_text_from_top_level_keys():
    assert app._extract_quantum_text({"response": "answer"}) == "answer"


def test_extract_quantum_text_from_choices_message():
    payload = {"choices": [{"message": {"content": "chat content"}}]}
    assert app._extract_quantum_text(payload) == "chat content"


def test_extract_quantum_text_from_choices_text():
    payload = {"choices": [{"text": "completion text"}]}
    assert app._extract_quantum_text(payload) == "completion text"


def test_extract_quantum_text_nested_data():
    payload = {"data": {"output_text": "deep value"}}
    assert app._extract_quantum_text(payload) == "deep value"


def test_extract_quantum_text_empty_for_unknown_shape():
    assert app._extract_quantum_text({"unknown": 123}) == ""
    assert app._extract_quantum_text(12345) == ""
