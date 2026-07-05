from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.unit
def test_pyppeteer_workflow_uses_supported_chromium_download_command() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "aria-tests.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "python -m pyppeteer install" not in content
    assert 'python -c "from pyppeteer.chromium_downloader import download_chromium; download_chromium()"' in content
