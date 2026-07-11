from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_DEVCONTAINER_DIR = Path(__file__).resolve().parents[1] / ".devcontainer"


def test_devcontainer_json_is_valid_json() -> None:
    """devcontainer.json must be valid JSON; the @devcontainers/cli parses it with JSON.parse()."""
    config_path = _DEVCONTAINER_DIR / "devcontainer.json"
    content = config_path.read_text(encoding="utf-8")
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f".devcontainer/devcontainer.json is not valid JSON: {exc}\n"
            "This will cause `devcontainer build` (and the build-and-test CI job) to fail."
        )


def test_devcontainer_lock_json_is_valid_json() -> None:
    """devcontainer-lock.json must be valid JSON with no trailing data.

    A stray closing brace after the root object caused:
        SyntaxError: Unexpected non-whitespace character after JSON at position 2143
    which broke the build-and-test devcontainer CI job.
    """
    lock_path = _DEVCONTAINER_DIR / "devcontainer-lock.json"
    if not lock_path.exists():
        pytest.skip("devcontainer-lock.json not present")
    content = lock_path.read_text(encoding="utf-8")
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f".devcontainer/devcontainer-lock.json is not valid JSON: {exc}\n"
            "Trailing or extra characters after the root object will cause "
            "`devcontainer build` (and the build-and-test CI job) to fail."
        )


def test_devcontainer_json_no_trailing_data() -> None:
    """Ensure no extra characters appear after the root JSON object in devcontainer.json."""
    config_path = _DEVCONTAINER_DIR / "devcontainer.json"
    content = config_path.read_text(encoding="utf-8").strip()
    parsed = json.loads(content)
    # Re-serialise and confirm round-trip is clean (catches extra non-whitespace data)
    assert isinstance(parsed, dict), "devcontainer.json root must be a JSON object"


def test_devcontainer_lock_json_no_trailing_data() -> None:
    """Ensure no extra characters appear after the root JSON object in devcontainer-lock.json."""
    lock_path = _DEVCONTAINER_DIR / "devcontainer-lock.json"
    if not lock_path.exists():
        pytest.skip("devcontainer-lock.json not present")
    content = lock_path.read_text(encoding="utf-8").strip()
    parsed = json.loads(content)
    assert isinstance(parsed, dict), "devcontainer-lock.json root must be a JSON object"
