from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def _load_workflow(workflow_name: str) -> dict:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / workflow_name
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def _workflow_triggers(workflow: dict) -> dict:
    # PyYAML parses an unquoted `on` key as boolean True per the YAML 1.1
    # rules, so support both parsed forms here.
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


def test_pages_workflow_concurrency_group() -> None:
    workflow = _load_workflow("pages.yml")
    concurrency = workflow.get("concurrency", {})

    assert concurrency.get("group") == "github-pages", (
        "pages.yml must use concurrency group 'github-pages' (not 'pages') so that "
        "manual runs are serialized with the same group that GitHub's built-in "
        "deploy-pages action recommends, preventing concurrent deploy conflicts."
    )
    assert concurrency.get("cancel-in-progress") is True, (
        "pages.yml concurrency must set cancel-in-progress: true so that a "
        "superseded manual run is cancelled rather than left running alongside "
        "a newer deployment."
    )
