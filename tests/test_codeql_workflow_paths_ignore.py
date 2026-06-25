from __future__ import annotations

from pathlib import Path

import pytest
import yaml


@pytest.mark.unit
def test_codeql_workflow_ignores_issue_template_changes() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "codeql.yml"
    assert workflow_path.exists(), "Expected CodeQL workflow to exist"

    workflow = yaml.load(workflow_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    assert ".github/ISSUE_TEMPLATE/**" in workflow["on"]["push"]["paths-ignore"]
    assert ".github/ISSUE_TEMPLATE/**" in workflow["on"]["pull_request"]["paths-ignore"]


@pytest.mark.unit
def test_codeql_autofix_ref_step_avoids_unbound_shell_vars() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "codeql.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert 'echo "ref=$ref_value"' not in content
    assert 'echo "repo=$repo_value"' not in content
    assert 'echo "can_push=$can_push_value"' not in content
