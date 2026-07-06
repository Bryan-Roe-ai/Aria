from __future__ import annotations

from pathlib import Path

import pytest


_DOWNLOAD_CMD = 'python -c "from pyppeteer.chromium_downloader import download_chromium; download_chromium()"'


@pytest.mark.unit
def test_pyppeteer_workflow_uses_supported_chromium_download_command() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "aria-tests.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "python -m pyppeteer install" not in content
    assert _DOWNLOAD_CMD in content


@pytest.mark.unit
def test_e2e_tests_workflow_uses_pyppeteer_bundled_chromium() -> None:
    """e2e-tests.yml containerized_chrome job must not try to apt-install chromium."""
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "e2e-tests.yml"
    content = workflow_path.read_text(encoding="utf-8")

    # Must use pyppeteer bundled download — never apt-install chromium-browser (not in Bullseye)
    assert "chromium-browser" not in content
    assert "python -m pyppeteer install" not in content
    assert _DOWNLOAD_CMD in content
