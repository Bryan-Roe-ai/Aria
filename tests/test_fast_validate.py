"""Tests for scripts/fast_validate.py severity behavior.

Ensures optional environment readiness gaps (e.g., no provider config) do not
cause hard validation failure, while critical repository issues still do.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_fast_validate_module():
    script_path = Path(__file__).parent.parent / "scripts" / "fast_validate.py"
    spec = importlib.util.spec_from_file_location("fast_validate", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_is_critical_failure_known_critical_statuses():
    mod = _load_fast_validate_module()

    assert mod.is_critical_failure("Datasets", "missing") is True
    assert mod.is_critical_failure("Scripts", "missing_scripts") is True
    assert mod.is_critical_failure("Dependencies", "missing_deps") is True


def test_is_critical_failure_optional_readiness_not_critical():
    mod = _load_fast_validate_module()

    # Optional readiness checks should be warnings, not hard failures
    assert mod.is_critical_failure("Virtual Envs", "no_venv") is False
    assert mod.is_critical_failure("Providers", "no_providers") is False


def test_is_critical_failure_ok_is_not_failure_for_any_check():
    mod = _load_fast_validate_module()

    checks = [
        "Datasets",
        "Scripts",
        "Virtual Envs",
        "Output Dirs",
        "Configs",
        "Providers",
        "Dependencies",
    ]
    for check in checks:
        assert mod.is_critical_failure(check, "ok") is False


def test_summarize_results_counts_ok_warning_and_critical():
    mod = _load_fast_validate_module()

    results = [
        {"check": "Datasets", "status": "ok"},
        {"check": "Providers", "status": "no_providers"},
        {"check": "Scripts", "status": "missing_scripts"},
    ]

    summary = mod.summarize_results(results)

    assert summary["total_checks"] == 3
    assert summary["ok_count"] == 1
    assert summary["warning_count"] == 1
    assert summary["critical_failure_count"] == 1
    assert summary["critical_failure_checks"] == ["Scripts"]


def test_summarize_results_no_critical_failures():
    mod = _load_fast_validate_module()

    results = [
        {"check": "Datasets", "status": "ok"},
        {"check": "Virtual Envs", "status": "no_venv"},
        {"check": "Providers", "status": "no_providers"},
    ]

    summary = mod.summarize_results(results)

    assert summary["total_checks"] == 3
    assert summary["ok_count"] == 1
    assert summary["warning_count"] == 2
    assert summary["critical_failure_count"] == 0
    assert summary["critical_failure_checks"] == []


def test_quick_check_venv_detects_dot_venv(tmp_path, monkeypatch):
    mod = _load_fast_validate_module()

    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    (tmp_path / ".venv" / "bin" / "python").write_text("#!/usr/bin/env python\n")

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    result = mod.quick_check_venv()

    assert result["status"] == "ok"
    assert result["venvs_found"] >= 1


def test_quick_check_dependencies_falls_back_to_project_venv(monkeypatch):
    mod = _load_fast_validate_module()

    class _FakeImportlibUtil:
        @staticmethod
        def find_spec(name: str):
            # Simulate missing only in current interpreter
            return None

    fake_venv_python = mod.REPO_ROOT / ".venv" / "bin" / "python"
    monkeypatch.setattr(mod, "_find_project_python", lambda: fake_venv_python)
    monkeypatch.setattr(mod, "_spec_exists_in_python", lambda _pkg, _py: True)

    # Patch importlib.util used inside quick_check_dependencies
    import importlib as _importlib

    monkeypatch.setattr(_importlib, "util", _FakeImportlibUtil)

    result = mod.quick_check_dependencies()

    assert result["status"] == "ok"
    assert set(result["missing"]) == set()
    assert "project_python" in result
