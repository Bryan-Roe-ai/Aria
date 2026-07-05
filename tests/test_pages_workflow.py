from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def _load_workflow(workflow_name: str) -> dict:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / workflow_name
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def test_pages_workflow_is_manual_only() -> None:
    workflow = _load_workflow("pages.yml")
    triggers = workflow.get("on", workflow.get(True, {}))

    assert "workflow_dispatch" in triggers
    assert "push" not in triggers, (
        "pages.yml must stay manual-only while GitHub Pages publishes /docs from "
        "the main branch; enabling a push trigger creates a duplicate deploy-pages "
        "job that races the built-in Pages deployment."
    )
