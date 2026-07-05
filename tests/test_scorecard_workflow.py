from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.mark.unit
def test_scorecard_workflow_uses_pinned_upload_sarif_action_sha() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "scorecard.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "REPLACE_WITH_FULL_40_CHAR_SHA" not in content
    assert "uses: github/codeql-action/upload-sarif@411c4c9a36b3fca4d674f06b6396b2c6d23522c6" in content
