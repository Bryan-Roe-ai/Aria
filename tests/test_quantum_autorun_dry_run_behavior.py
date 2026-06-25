"""Behavioral tests for quantum autorun dry-run validation."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from quantum_autorun import QJob, dry_run_jobs  # noqa: E402


def test_dry_run_jobs_skips_disabled_qpu_but_validates_local_job():
    jobs = [
        QJob(name="local_ok", preset="heart", enabled=True),
        QJob(
            name="paid_qpu_disabled",
            mode="azure_hardware",
            azure_backend="ionq.qpu",
            azure_confirm_cost=False,
            enabled=False,
        ),
    ]

    results, failures = dry_run_jobs(jobs)

    assert failures == []
    assert results[0]["status"] == "validated"
    assert results[1]["status"] == "skipped"
    assert results[1]["reason"] == "disabled"
