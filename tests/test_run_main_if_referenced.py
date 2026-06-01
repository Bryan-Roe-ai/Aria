"""Tests for run_main_if_referenced.py entrypoint helper."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_module():
    script_path = Path(__file__).parent.parent / "run_main_if_referenced.py"
    spec = importlib.util.spec_from_file_location("run_main_if_referenced", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_does_not_call_main_when_not_main():
    mod = _load_module()
    called = []

    def fake_main():
        called.append(True)
        return 0

    # __name__ is not "__main__" so main must not run and no SystemExit raised.
    mod.run_main_if_referenced("some_module", fake_main)
    assert called == []


def test_calls_main_and_exits_with_return_code():
    mod = _load_module()
    called = []

    def fake_main():
        called.append(True)
        return 7

    with pytest.raises(SystemExit) as excinfo:
        mod.run_main_if_referenced("__main__", fake_main)

    assert called == [True]
    assert excinfo.value.code == 7


def test_exit_code_zero_when_main_returns_zero():
    mod = _load_module()

    with pytest.raises(SystemExit) as excinfo:
        mod.run_main_if_referenced("__main__", lambda: 0)

    assert excinfo.value.code == 0
