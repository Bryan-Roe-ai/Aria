from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


WORKFLOW_FILES = [
    ".github/workflows/ci.yml",
    ".github/workflows/pr-checks.yml",
]


def _load_yaml(relative_path: str) -> dict:
    root = Path(__file__).resolve().parents[1]
    path = root / relative_path
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _iter_step_uses(workflow: dict) -> list[str]:
    uses_values: list[str] = []
    jobs = workflow.get("jobs", {})
    for job in jobs.values():
        for step in job.get("steps", []):
            uses = step.get("uses")
            if isinstance(uses, str):
                uses_values.append(uses)
    return uses_values


@pytest.mark.parametrize("workflow_path", WORKFLOW_FILES)
def test_workflow_uses_setup_verify_action(workflow_path: str) -> None:
    workflow = _load_yaml(workflow_path)
    uses_values = _iter_step_uses(workflow)

    assert "./.github/actions/run-setup-verify" in uses_values
