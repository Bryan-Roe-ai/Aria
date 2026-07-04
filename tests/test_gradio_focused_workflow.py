from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests.workflow_test_helpers import (
    EXPECTED_HARDEN_RUNNER_ACTION,
    EXPECTED_SETUP_PYTHON_ACTION,
)


@pytest.mark.unit
def test_gradio_focused_workflow_uses_hardened_runner_and_bash_shell() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "gradio-focused-tests.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    steps = workflow["jobs"]["gradio-focused"]["steps"]
    assert workflow["permissions"]["contents"] == "read"
    assert workflow["defaults"]["run"]["shell"] == "bash"
    assert workflow["jobs"]["gradio-focused"]["timeout-minutes"] == 10
    assert steps[0]["name"] == "Harden runner"
    assert steps[0]["uses"] == EXPECTED_HARDEN_RUNNER_ACTION
    assert steps[0]["with"]["egress-policy"] == "audit"
    assert steps[0]["with"]["disable-sudo"] is True
    assert steps[1]["uses"] == "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"
    assert steps[1]["with"]["persist-credentials"] is False


@pytest.mark.unit
def test_gradio_focused_workflow_uses_reusable_python_setup_without_repo_requirements() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "gradio-focused-tests.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    setup_step = next(
        step for step in workflow["jobs"]["gradio-focused"]["steps"] if step.get("uses") == EXPECTED_SETUP_PYTHON_ACTION
    )
    assert setup_step["uses"] == EXPECTED_SETUP_PYTHON_ACTION
    assert setup_step["with"]["install-requirements"] == "false"
    assert setup_step["with"]["install-dev-requirements"] == "false"
    assert setup_step["with"]["extra-packages"] == "pytest gradio"
