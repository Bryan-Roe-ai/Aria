from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def _load_merge_gate() -> dict:
    workflow_path = Path(__file__).resolve().parents[1] / ".github/workflows/merge-gate.yml"
    return yaml.safe_load(workflow_path.read_text(encoding="utf-8"))


def test_merge_gate_defines_setup_guardrails_job() -> None:
    workflow = _load_merge_gate()
    jobs = workflow["jobs"]

    assert "setup-guardrails" in jobs
    assert jobs["setup-guardrails"]["name"] == "Setup Guardrails"


def test_merge_gate_fan_in_requires_setup_guardrails() -> None:
    workflow = _load_merge_gate()
    gates_passed = workflow["jobs"]["gates-passed"]

    assert "setup-guardrails" in gates_passed["needs"]
