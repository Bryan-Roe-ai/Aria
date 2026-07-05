from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def test_scorecard_workflow_uses_pinned_upload_sarif_action() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "scorecard.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    upload_step = next(step for step in workflow["jobs"]["analysis"]["steps"] if step["name"] == "Upload to code scanning")
    assert upload_step["uses"] == "github/codeql-action/upload-sarif@4e828ff8d448a8a6e532957b1811f387a63867e8"
    assert "REPLACE_WITH_FULL_40_CHAR_SHA" not in upload_step["uses"]
