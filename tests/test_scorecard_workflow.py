from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.mark.unit
def test_scorecard_workflow_pins_valid_upload_sarif_sha() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "scorecard.yml"
    assert workflow_path.exists(), "Expected scorecard workflow to exist"

    content = workflow_path.read_text(encoding="utf-8")

    assert "github/codeql-action/upload-sarif@REPLACE_WITH_FULL_40_CHAR_SHA" not in content
    assert re.search(r"uses:\s+github/codeql-action/upload-sarif@[0-9a-f]{40}\b", content)
