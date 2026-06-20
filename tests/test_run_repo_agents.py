"""Tests for scripts/run_repo_agents.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agents.base import AgentResult  # noqa: E402
from scripts import run_repo_agents as runner  # noqa: E402


def test_run_agents_executes_registered_agents(tmp_path, monkeypatch):
    class _FakeAgent:
        name = "fake-agent"

        def run(self) -> AgentResult:
            return AgentResult(
                name=self.name,
                status="ok",
                summary="fake ok",
            )

        def write_status(self, result: AgentResult) -> Path:
            path = tmp_path / "agents" / self.name / "status.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(result.to_dict()), encoding="utf-8")
            return path

    monkeypatch.setattr(runner, "_AGENT_MODULES", ())
    monkeypatch.setattr(runner, "get_registered_agents", lambda: {"fake-agent": _FakeAgent})

    results, summary = runner.run_agents(dry_run=True)

    assert len(results) == 1
    assert results[0].name == "fake-agent"
    assert summary.agents_run == 1
    assert summary.ok == 1
    assert summary.succeeded is True


def test_main_returns_one_on_error_status(monkeypatch):
    class _BadAgent:
        name = "bad-agent"

        def run(self) -> AgentResult:
            return AgentResult(name=self.name, status="error", summary="broken")

        def write_status(self, _result: AgentResult) -> Path:
            return Path("/dev/null")

    monkeypatch.setattr(runner, "_AGENT_MODULES", ())
    monkeypatch.setattr(runner, "get_registered_agents", lambda: {"bad-agent": _BadAgent})
    monkeypatch.setattr(runner, "write_summary", lambda summary: Path("/dev/null"))

    assert runner.main(["--dry-run"]) == 0
    assert runner.main(["--dry-run", "--fail-on-error"]) == 1


def test_main_fail_on_warning(monkeypatch):
    class _WarnAgent:
        name = "warn-agent"

        def run(self) -> AgentResult:
            return AgentResult(name=self.name, status="warning", summary="heads up")

        def write_status(self, _result: AgentResult) -> Path:
            return Path("/dev/null")

    monkeypatch.setattr(runner, "_AGENT_MODULES", ())
    monkeypatch.setattr(runner, "get_registered_agents", lambda: {"warn-agent": _WarnAgent})
    monkeypatch.setattr(runner, "write_summary", lambda summary: Path("/dev/null"))

    assert runner.main(["--dry-run"]) == 0
    assert runner.main(["--dry-run", "--fail-on-warning"]) == 1
