from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _load_module():
    module_path = Path(__file__).resolve().parents[1] / "examples" / "ai_starters" / "agent_with_tools.py"
    spec = importlib.util.spec_from_file_location(
        "agent_with_tools_example",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_calculator_supports_basic_precedence_and_negative_values():
    module = _load_module()

    assert module.calculator_tool("2 + 3 * 4") == "14.0"
    assert module.calculator_tool("-5 + 2") == "-3.0"


def test_calculator_reports_unsupported_expression():
    module = _load_module()

    result = module.calculator_tool("sum([1, 2, 3])")

    assert result.startswith("Calculation error:")


def test_read_and_write_tools_stay_within_workspace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module = _load_module()
    monkeypatch.setattr(module, "_FILE_TOOL_ROOT", tmp_path)

    write_result = module.write_file_tool("notes/output.txt", "hello")
    read_result = module.read_file_tool("notes/output.txt")
    blocked_result = module.write_file_tool("../escape.txt", "nope")

    assert "Wrote 5 chars" in write_result
    assert read_result == "hello"
    assert blocked_result.startswith("File access error:")


def test_long_reads_are_truncated_with_marker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    module = _load_module()
    monkeypatch.setattr(module, "_FILE_TOOL_ROOT", tmp_path)
    long_file = tmp_path / "long.txt"
    long_file.write_text("a" * 2100, encoding="utf-8")

    result = module.read_file_tool("long.txt")

    assert result.endswith("\n...[truncated]")
    assert len(result) > 2000


def test_route_rejects_malformed_write_command():
    module = _load_module()
    agent = module.ToolAgent(corpus=["alpha", "beta"])

    tool_name, fn, args = agent.route("write: missing separator")

    assert tool_name == "error"
    assert fn(*args) == "Use: write: <path> | <content>"
