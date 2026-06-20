"""Tests for the Aria quantum integration bridge."""

from __future__ import annotations

import asyncio
import json
import types
from pathlib import Path

import pytest

from mount.quantum_integration import QuantumIntegration


def _make_config(tmp_path: Path) -> dict:
    return {
        "paths": {
            "workspace_root": str(tmp_path),
            "quantum_ai": str(tmp_path / "quantum-ai"),
        },
        "quantum": {
            "enabled": True,
            "default_backend": "qiskit_aer",
        },
    }


def _stub_subprocess(returncode: int = 0, stdout: str = "ok", stderr: str = ""):
    return types.SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


@pytest.mark.unit
@pytest.mark.parametrize(
    "jobs_payload,expected_preset",
    [
        ([{"name": "baseline", "preset": "heart", "status": "completed"}], "heart"),
        ({"baseline": {"name": "baseline", "preset": "heart", "status": "completed"}}, "heart"),
    ],
)
def test_run_autorun_job_reads_status_for_list_and_dict_shapes(tmp_path: Path, monkeypatch, jobs_payload, expected_preset):
    quantum_root = tmp_path / "quantum-ai"
    quantum_root.mkdir(parents=True, exist_ok=True)
    status_file = tmp_path / "data_out" / "quantum_autorun" / "status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(
        {"jobs": jobs_payload, "timestamp": "2026-06-20T00:00:00Z"}))

    integration = QuantumIntegration(_make_config(tmp_path))
    monkeypatch.setattr("mount.quantum_integration.subprocess.run",
                        lambda *args, **kwargs: _stub_subprocess())

    result = asyncio.run(integration.run_autorun_job("baseline", dry_run=True))

    assert result["success"] is True
    assert result["job_name"] == "baseline"
    assert result["dry_run"] is True
    assert result["status"]["preset"] == expected_preset
    assert result["status"]["name"] == "baseline"
