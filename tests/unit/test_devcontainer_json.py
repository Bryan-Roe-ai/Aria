"""Regression test: .devcontainer JSON files must be valid JSON.

Guard against a past failure where a stray closing brace was appended to
devcontainer-lock.json, causing the devcontainers CLI to abort with:
  SyntaxError: Unexpected non-whitespace character after JSON at position 2143

See: GitHub Actions run 29139965422, job 86511118286.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEVCONTAINER_DIR = REPO_ROOT / ".devcontainer"


def test_devcontainer_json_is_valid():
    path = DEVCONTAINER_DIR / "devcontainer.json"
    assert path.exists(), f"{path} not found"
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"devcontainer.json is invalid JSON: {exc}") from exc


def test_devcontainer_lock_json_is_valid():
    path = DEVCONTAINER_DIR / "devcontainer-lock.json"
    assert path.exists(), f"{path} not found"
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"devcontainer-lock.json is invalid JSON: {exc}\n"
            "Hint: check for a stray closing brace or bracket at the end of the file."
        ) from exc


def test_devcontainer_lock_json_has_features_key():
    path = DEVCONTAINER_DIR / "devcontainer-lock.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "features" in data, "devcontainer-lock.json missing top-level 'features' key"
