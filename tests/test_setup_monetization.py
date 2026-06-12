"""Unit tests for setup_monetization.py helper functions.

Focuses on the deterministic, side-effect-light helpers: file existence
checks, dependency probing, and local.settings.json scaffolding.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path


def _load_module():
    script_path = Path(__file__).parent.parent / "setup_monetization.py"
    spec = importlib.util.spec_from_file_location("setup_monetization", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_check_file_exists_true_and_false(tmp_path):
    mod = _load_module()
    existing = tmp_path / "present.txt"
    existing.write_text("x")

    assert mod.check_file_exists(str(existing)) is True
    assert mod.check_file_exists(str(tmp_path / "absent.txt")) is False


def test_check_python_imports_true_for_stdlib(capsys):
    mod = _load_module()
    # All probed modules (json, datetime, enum, pathlib) are stdlib.
    assert mod.check_python_imports() is True


def test_create_local_settings_creates_file(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.chdir(tmp_path)

    assert not (tmp_path / "local.settings.json").exists()
    result = mod.create_local_settings()

    assert result is True
    settings_path = tmp_path / "local.settings.json"
    assert settings_path.exists()

    data = json.loads(settings_path.read_text())
    assert data["IsEncrypted"] is False
    assert data["Values"]["FUNCTIONS_WORKER_RUNTIME"] == "python"
    assert "QAI_DB_CONN" in data["Values"]


def test_create_local_settings_is_idempotent(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.chdir(tmp_path)

    sentinel = {"IsEncrypted": False, "Values": {"CUSTOM": "keep-me"}}
    (tmp_path / "local.settings.json").write_text(json.dumps(sentinel))

    result = mod.create_local_settings()

    assert result is True
    # Existing file must not be overwritten.
    data = json.loads((tmp_path / "local.settings.json").read_text())
    assert data == sentinel
