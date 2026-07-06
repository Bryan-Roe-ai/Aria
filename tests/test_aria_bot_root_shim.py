"""Tests for the repository-root ``aria_bot`` compatibility shim."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_root_aria_bot_shim():
    init_path = REPO_ROOT / "aria_bot" / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "aria_bot_root_shim_under_test",
        init_path,
        submodule_search_locations=[str(init_path.parent)],
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_root_aria_bot_shim_reexports_public_api():
    module = _load_root_aria_bot_shim()

    assert hasattr(module, "__all__")
    assert "run_cycle" in module.__all__
    assert hasattr(module, "run_cycle")
    assert hasattr(module, "DEFAULT_MAX_PLANS")


def test_python_dash_m_aria_bot_works_from_repo_root():
    result = subprocess.run(
        [sys.executable, "-m", "aria_bot", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "self-modifying repository cycle" in result.stdout


@pytest.mark.skipif(
    sys.platform == "win32", reason="Shell script execute bit and direct .sh execution not applicable on Windows"
)
def test_start_aria_bot_shell_wrapper_works_from_repo_root():
    script = REPO_ROOT / "scripts" / "start_aria_bot.sh"

    assert script.exists()
    assert script.stat().st_mode & 0o111

    result = subprocess.run(
        [str(script), "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "self-modifying repository cycle" in result.stdout
