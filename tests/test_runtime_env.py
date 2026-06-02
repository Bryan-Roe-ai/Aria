from __future__ import annotations

import json
import subprocess

from shared.runtime_env import build_venv_info, locate_project_python


def test_locate_project_python_prefers_dot_venv_linux_layout(tmp_path):
    python_path = tmp_path / ".venv" / "bin" / "python"
    python_path.parent.mkdir(parents=True)
    python_path.write_text("#!/usr/bin/env python3\n")

    assert locate_project_python(tmp_path) == python_path


def test_build_venv_info_uses_existing_python_and_caches_probe(tmp_path, monkeypatch):
    python_path = tmp_path / "venv" / "bin" / "python"
    python_path.parent.mkdir(parents=True)
    python_path.write_text("#!/usr/bin/env python3\n")

    calls: list[list[str]] = []

    class _Proc:
        returncode = 0
        stdout = json.dumps(
            {
                "available": {"torch": True, "transformers": False, "peft": True},
                "versions": {"torch": "1.0", "transformers": None, "peft": "2.0"},
            }
        )
        stderr = ""

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _Proc()

    monkeypatch.setattr("shared.runtime_env.subprocess.run", fake_run)

    info = build_venv_info(tmp_path, timeout_seconds=1)

    assert info["path"] == str(python_path)
    assert info["exists"] is True
    assert info["packages"]["available"]["torch"] is True
    assert info["packages"]["versions"]["peft"] == "2.0"
    assert len(calls) == 1


def test_build_venv_info_reports_missing_python(tmp_path):
    info = build_venv_info(tmp_path)

    assert info["exists"] is False
    assert info["packages"] == {}
    assert "python" in str(info["path"]).lower()


def test_build_venv_info_handles_malformed_probe_output(tmp_path, monkeypatch):
    python_path = tmp_path / "venv" / "bin" / "python"
    python_path.parent.mkdir(parents=True)
    python_path.write_text("#!/usr/bin/env python3\n")

    class _Proc:
        returncode = 0
        stdout = "not-json"
        stderr = ""

    def fake_run(cmd, **kwargs):
        return _Proc()

    monkeypatch.setattr("shared.runtime_env.subprocess.run", fake_run)

    info = build_venv_info(tmp_path, timeout_seconds=1)

    assert info["exists"] is True
    assert info["packages"]["available"]["torch"] is False
    assert "JSON decode failed" in str(info["error"])


def test_build_venv_info_handles_probe_timeout(tmp_path, monkeypatch):
    python_path = tmp_path / "venv" / "bin" / "python"
    python_path.parent.mkdir(parents=True)
    python_path.write_text("#!/usr/bin/env python3\n")

    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"])

    monkeypatch.setattr("shared.runtime_env.subprocess.run", fake_run)

    info = build_venv_info(tmp_path, timeout_seconds=1)

    assert info["exists"] is True
    assert info["packages"]["available"]["torch"] is False
    assert "Probe timed out" in str(info["error"])
