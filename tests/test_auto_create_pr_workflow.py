from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.unit
def test_auto_create_pr_workflow_pins_valid_github_script_sha() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-create-pr.yml"
    assert workflow_path.exists(), "Expected auto-create-pr workflow to exist"

    content = workflow_path.read_text(encoding="utf-8")

    assert "GITHUB_SCRIPT_SHA: 6c7412b91e94c06da7a44f7005215554601ef463e" not in content
    assert "GITHUB_SCRIPT_SHA: 60a0d83039c74a4aee543508d2ffcb1c3799cdea" in content
    assert "uses: actions/github-script@60a0d83039c74a4aee543508d2ffcb1c3799cdea" in content
