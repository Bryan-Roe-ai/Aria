from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "training-health-report.yml"


def _extract_status_script() -> str:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    marker = "python3 - << 'PYEOF'\n"
    start = text.index(marker) + len(marker)
    end = text.index("\n          PYEOF", start)
    return textwrap.dedent(text[start:end]).strip()


def test_checkout_step_has_submodules_false() -> None:
    """Regression guard: checkout step must have submodules: false.

    Without explicit ``submodules: false``, an orphaned gitlink in the tree
    (e.g. LMStudio-MCP) causes ``git submodule foreach --recursive`` to fail
    during the credential-removal post-processing of actions/checkout, even
    though submodules are not being fetched.  See CI job 84021614545.
    """
    wf = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    steps = wf["jobs"]["health-report"]["steps"]
    checkout_steps = [s for s in steps if "checkout" in (s.get("uses") or "").lower()]
    assert checkout_steps, "No checkout step found in training-health-report.yml"
    for step in checkout_steps:
        with_cfg = step.get("with", {})
        assert with_cfg.get("submodules") is False, (
            f"Checkout step '{step.get('name', '(unnamed)')}' must set "
            f"submodules: false to prevent orphaned-gitlink checkout failures"
        )


def _run_status_script(tmp_path: Path, training: dict) -> dict:
    (tmp_path / "data_out").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data_out" / "autonomous_training_status.json").write_text(json.dumps(training), encoding="utf-8")

    github_output = tmp_path / "github_output.txt"
    env = os.environ.copy()
    env["GITHUB_OUTPUT"] = str(github_output)

    proc = subprocess.run(
        [sys.executable, "-c", _extract_status_script()],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )

    assert proc.returncode == 0, proc.stderr
    pairs = {}
    for line in github_output.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            pairs[key] = value
    return pairs


def test_no_training_attempt_is_no_data_not_degraded(tmp_path: Path) -> None:
    outputs = _run_status_script(
        tmp_path,
        {
            "cycles_completed": 0,
            "best_accuracy": 0.0,
            "performance_history": [],
            "dataset_inventory": {},
        },
    )

    assert outputs["no_data"] == "true"
    assert outputs["degraded"] == "false"


def test_low_accuracy_after_training_is_degraded(tmp_path: Path) -> None:
    outputs = _run_status_script(
        tmp_path,
        {
            "cycles_completed": 1,
            "best_accuracy": 0.2,
            "performance_history": [{"accuracy": 0.2}],
            "dataset_inventory": {},
        },
    )

    assert outputs["no_data"] == "false"
    assert outputs["degraded"] == "true"
