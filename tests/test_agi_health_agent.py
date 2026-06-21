"""Tests for the AGI health automation agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agents.agi_health_agent import AgiHealthAgent, main  # noqa: E402


def test_agi_health_runs_and_reports_metrics():
    result = AgiHealthAgent().run()

    assert result.name == "agi-health"
    assert result.status in {"ok", "warning", "error"}
    assert "registry_size" in result.metrics


def test_missing_canonical_provider_is_error(tmp_path, monkeypatch):
    agent = AgiHealthAgent(repo_root=tmp_path)
    missing = tmp_path / "missing" / "agi_provider.py"
    monkeypatch.setattr("scripts.agents.agi_health_agent.CANONICAL_PATHS", (missing,))
    monkeypatch.setattr("scripts.agents.agi_health_agent.CANONICAL_PROVIDER", missing)

    result = agent.run()

    assert result.status == "error"
    assert any(f["issue"] == "missing_path" for f in result.findings)


def test_main_json_dry_run(capsys):
    code = main(["--dry-run", "--json"])
    assert code in {0, 1}
    payload = json.loads(capsys.readouterr().out)
    assert payload["name"] == "agi-health"
