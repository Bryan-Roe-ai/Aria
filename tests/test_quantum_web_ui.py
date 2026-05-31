"""Regression checks for the quantum dashboard web UI."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip("flask", reason="flask is not installed")

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_APP_PATH = REPO_ROOT / "ai-projects" / "quantum-ml" / "web_app.py"
INDEX_PATH = REPO_ROOT / "ai-projects" / "quantum-ml" / "web_ui" / "index.html"
APP_JS_PATH = REPO_ROOT / "ai-projects" / "quantum-ml" / "web_ui" / "static" / "app.js"


def _load_web_app():
    spec = importlib.util.spec_from_file_location("quantum_web_app_ui_tests", WEB_APP_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {WEB_APP_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def client():
    module = _load_web_app()
    module.app.config["TESTING"] = True
    with module.app.test_client() as test_client:
        yield test_client


def test_dashboard_root_includes_overview_and_details_panel(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert 'id="overview-datasets"' in body
    assert 'id="result-details"' in body
    assert 'id="toast-container"' in body


def test_dashboard_index_contains_dataset_guidance_region() -> None:
    body = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="dataset-guidance"' in body
    assert 'id="dataset-guidance-text"' in body


def test_dashboard_script_uses_toasts_instead_of_alerts() -> None:
    script = APP_JS_PATH.read_text(encoding="utf-8")

    assert "function showToast(" in script
    assert "alert(" not in script
