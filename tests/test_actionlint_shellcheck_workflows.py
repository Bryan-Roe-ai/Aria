from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.unit
def test_e2e_summary_avoids_sc2129_multiple_append_redirects() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "e2e-tests.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert 'echo "## Core Runtime Monitor" >> "$GITHUB_STEP_SUMMARY"' not in content
    assert '} >> "$GITHUB_STEP_SUMMARY"' in content


@pytest.mark.unit
def test_repo_cleanup_report_avoids_sc2129_multiple_append_redirects() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "repo-cleanup.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "echo '# Repository Cleanup Report' > docs/reports/repo-health.md" not in content
    assert "} > docs/reports/repo-health.md" in content
