"""Run Node-based unit tests for apps/chat/static/agi_stream_utils.js."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
JS_TEST = REPO_ROOT / "tests" / "js" / "test_agi_stream_utils.mjs"


@pytest.mark.unit
def test_agi_stream_utils_js_harness():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node executable not available")

    proc = subprocess.run(
        [node, "--test", str(JS_TEST)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
