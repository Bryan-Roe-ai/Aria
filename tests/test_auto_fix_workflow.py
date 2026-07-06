from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def _load_workflow() -> dict:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "auto-fix.yml"
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def test_auto_fix_ruff_autofix_is_non_blocking() -> None:
    workflow = _load_workflow()
    step = next(step for step in workflow["jobs"]["autofix"]["steps"] if step["name"] == "Run Ruff autofixes")
    assert "--fix --exit-zero" in step["run"]


def test_auto_fix_quality_gates_are_best_effort() -> None:
    workflow = _load_workflow()
    steps = {step["name"]: step for step in workflow["jobs"]["autofix"]["steps"]}

    assert steps["Run Black formatting"]["continue-on-error"] is True
    assert steps["Verify Ruff"]["continue-on-error"] is True
    assert steps["Verify Black"]["continue-on-error"] is True
    assert steps["Run targeted pytest"]["continue-on-error"] is True
