"""Tests for the AGENTS.md audit automation agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agents.agents_md_audit_agent import AgentsMdAuditAgent, main  # noqa: E402

VALID_AGENTS_MD = """\
# AGENTS

## Learned User Preferences

- Commit messages follow conventional format.
- PR bodies use standard headers.

## Learned Workspace Facts

- Unit test suite passes 2700 tests (as of 2026-06-20).
- Automation agent framework lives in scripts/agents/.
"""


def test_valid_agents_md_passes(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(VALID_AGENTS_MD, encoding="utf-8")

    result = AgentsMdAuditAgent(repo_root=tmp_path, agents_md_path=agents_md).run()

    assert result.status == "ok"
    assert result.metrics["preferences_bullets"] == 2
    assert result.metrics["facts_bullets"] == 2
    assert result.findings == []


def test_missing_file_is_error(tmp_path):
    missing = tmp_path / "AGENTS.md"

    result = AgentsMdAuditAgent(repo_root=tmp_path, agents_md_path=missing).run()

    assert result.status == "error"
    assert result.findings[0]["kind"] == "missing_file"


def test_missing_section_is_error(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(
        "## Learned User Preferences\n\n- One preference.\n",
        encoding="utf-8",
    )

    result = AgentsMdAuditAgent(repo_root=tmp_path, agents_md_path=agents_md).run()

    assert result.status == "error"
    assert any(f["kind"] == "missing_section" for f in result.findings)


def test_bullet_limit_warning(tmp_path):
    bullets = "\n".join(f"- Bullet {index}." for index in range(13))
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(
        f"## Learned User Preferences\n\n{bullets}\n\n## Learned Workspace Facts\n\n- One fact.\n",
        encoding="utf-8",
    )

    result = AgentsMdAuditAgent(repo_root=tmp_path, agents_md_path=agents_md).run()

    assert result.status == "warning"
    assert any(f["kind"] == "bullet_limit" for f in result.findings)


def test_merge_conflict_is_warning(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(
        "## Learned User Preferences\n\n- ok\n<<<<<<< HEAD\n\n## Learned Workspace Facts\n\n- ok\n",
        encoding="utf-8",
    )

    result = AgentsMdAuditAgent(repo_root=tmp_path, agents_md_path=agents_md).run()

    assert result.status == "warning"
    assert any(f["kind"] == "merge_conflict" for f in result.findings)


def test_secret_pattern_is_warning(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(
        "## Learned User Preferences\n\n- Use sk-abcdefghijklmnopqrstuvwxyz123456 for auth.\n\n"
        "## Learned Workspace Facts\n\n- One fact.\n",
        encoding="utf-8",
    )

    result = AgentsMdAuditAgent(repo_root=tmp_path, agents_md_path=agents_md).run()

    assert result.status == "warning"
    assert any(f["kind"] == "secret_pattern" for f in result.findings)


def test_stale_date_warning(tmp_path):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(
        "## Learned User Preferences\n\n- One preference.\n\n"
        "## Learned Workspace Facts\n\n- Tests pass as of 2020-01-01.\n",
        encoding="utf-8",
    )

    result = AgentsMdAuditAgent(
        repo_root=tmp_path,
        agents_md_path=agents_md,
        stale_date_days=30,
    ).run()

    assert result.status == "warning"
    assert any(f["kind"] == "stale_date" for f in result.findings)
    assert result.metrics["stale_dates"] == 1


def test_dry_run_does_not_write_status(tmp_path, monkeypatch, capsys):
    import scripts.agents.base as base

    monkeypatch.setattr(base, "AGENTS_DATA_DIR", tmp_path / "agent-status")
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(VALID_AGENTS_MD, encoding="utf-8")
    status_path = tmp_path / "agent-status" / "agents-md-audit" / "status.json"

    assert main(["--root", str(tmp_path), "--agents-md", str(agents_md), "--dry-run"]) == 0
    assert not status_path.exists()

    assert main(["--root", str(tmp_path), "--agents-md", str(agents_md)]) == 0
    assert status_path.exists()
    loaded = json.loads(status_path.read_text(encoding="utf-8"))
    assert loaded["name"] == "agents-md-audit"
    capsys.readouterr()


def test_json_flag_prints_full_result(tmp_path, capsys):
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text(VALID_AGENTS_MD, encoding="utf-8")

    assert main(["--root", str(tmp_path), "--agents-md", str(agents_md), "--dry-run", "--json"]) == 0

    printed = json.loads(capsys.readouterr().out)
    assert printed["name"] == "agents-md-audit"
    assert printed["status"] == "ok"
