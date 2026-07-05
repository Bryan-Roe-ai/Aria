from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def _load_workflow(workflow_name: str) -> dict:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / workflow_name
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def _workflow_triggers(workflow: dict) -> dict:
    # PyYAML still treats an unquoted `on` key as a YAML 1.1 boolean in GitHub
    # workflow files, so support both parsed forms here.
    return workflow.get("on") or workflow.get(True, {})


def test_pages_workflow_is_manual_only() -> None:
    workflow = _load_workflow("pages.yml")
    triggers = _workflow_triggers(workflow)

    assert "workflow_dispatch" in triggers
    assert "push" not in triggers, (
        "pages.yml must stay manual-only while GitHub Pages publishes /docs from "
        "the main branch; enabling a push trigger creates a duplicate deploy-pages "
        "job that races the built-in Pages deployment."
    )
