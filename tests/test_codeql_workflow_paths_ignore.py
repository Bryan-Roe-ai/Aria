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
