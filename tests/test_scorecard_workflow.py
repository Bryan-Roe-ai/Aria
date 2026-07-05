from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def _load_workflow(workflow_name: str) -> dict:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / workflow_name
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def test_scorecard_workflow_uses_pinned_upload_sarif_action() -> None:
    workflow = _load_workflow("scorecard.yml")
    codeql_workflow = _load_workflow("codeql.yml")

    upload_step = next(
        step for step in workflow["jobs"]["analysis"]["steps"] if step["name"] == "Upload to code scanning"
    )
    codeql_init_step = next(
        step
        for step in codeql_workflow["jobs"]["analyze"]["steps"]
        if step.get("uses", "").startswith("github/codeql-action/init@")
    )
    _action_ref, separator, expected_sha = codeql_init_step["uses"].rpartition("@")

    assert separator == "@"
    assert upload_step["uses"] == f"github/codeql-action/upload-sarif@{expected_sha}"
    assert "REPLACE_WITH_FULL_40_CHAR_SHA" not in upload_step["uses"]
