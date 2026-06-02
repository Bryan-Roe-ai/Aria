"""Focused tests for the core CLI entrypoint."""

from __future__ import annotations

import json

import pytest

import core.__main__ as core_main


def test_build_parser_defaults() -> None:
    args = core_main._build_parser().parse_args([])

    assert args.cycles == 1
    assert args.sleep == 0.1


def test_main_runs_once_and_prints_summary(monkeypatch, capsys) -> None:
    class _Runner:
        def __init__(self, config):
            self.config = config
            self.run_once_called = False
            self.run_called = False

        def run_once(self):
            self.run_once_called = True
            return {"goal": "improve"}

        def run(self):
            self.run_called = True

    constructed: list[_Runner] = []

    def _factory(config):
        runner = _Runner(config)
        constructed.append(runner)
        return runner

    monkeypatch.setattr(core_main, "AriaRunner", _factory)

    core_main.main(["--cycles", "1", "--sleep", "0.25"])

    runner = constructed[0]
    assert runner.config == {"max_cycles": 1, "sleep_seconds": 0.25}
    assert runner.run_once_called is True
    assert runner.run_called is False
    assert json.loads(capsys.readouterr().out) == {"goal": "improve"}


def test_main_runs_full_loop_for_multiple_cycles(monkeypatch) -> None:
    class _Runner:
        def __init__(self, config):
            self.config = config
            self.run_once_called = False
            self.run_called = False

        def run_once(self):
            self.run_once_called = True
            return {"goal": "improve"}

        def run(self):
            self.run_called = True

    constructed: list[_Runner] = []

    def _factory(config):
        runner = _Runner(config)
        constructed.append(runner)
        return runner

    monkeypatch.setattr(core_main, "AriaRunner", _factory)

    core_main.main(["--cycles", "2", "--sleep", "0.5"])

    runner = constructed[0]
    assert runner.config == {"max_cycles": 2, "sleep_seconds": 0.5}
    assert runner.run_once_called is False
    assert runner.run_called is True


def test_main_rejects_invalid_cycle_count() -> None:
    with pytest.raises(SystemExit, match="--cycles must be at least 1"):
        core_main.main(["--cycles", "0"])
