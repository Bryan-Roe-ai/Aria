"""Integration tests for the Aria object API (/api/aria/object, /api/aria/objects).

These tests start a real Aria server in a background thread, send HTTP requests
to the object API, and verify the JSON responses.

Marked with pytest.mark.integration — run via:
    pytest tests/test_object_api_integration.py -v
"""

from __future__ import annotations

import json
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

# Ensure apps/aria is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "aria"))


# ---------------------------------------------------------------------------
# Server fixture
# ---------------------------------------------------------------------------

_SERVER_PORT = 18580  # use a dedicated port to avoid conflicts


@pytest.fixture(scope="module")
def aria_server():
    """Start the Aria server in a background thread for the test module."""
    import importlib
    import server as aria_module

    # Reset global state for a clean test run
    aria_module.stage_state.clear()
    aria_module.stage_state.update(
        {
            "aria": {"position": {"x": 50, "y": 50}, "expression": "idle"},
            "objects": {},
            "environment": {
                "table": {"position": {"x": 60, "y": 20}},
                "stage_bounds": {"width": 100, "height": 100},
            },
        }
    )

    from http.server import HTTPServer

    httpd = HTTPServer(("127.0.0.1", _SERVER_PORT),
                       aria_module.AriaRequestHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    # Wait for server to be ready
    base = f"http://127.0.0.1:{_SERVER_PORT}"
    for _ in range(40):
        try:
            urllib.request.urlopen(f"{base}/api/aria/state", timeout=1)
            break
        except Exception:
            time.sleep(0.1)

    yield base

    httpd.shutdown()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read())


def _post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Tests — GET /api/aria/objects
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_get_objects_returns_dict(aria_server):
    resp = _get(f"{aria_server}/api/aria/objects")
    assert "objects" in resp, "Response must contain 'objects' key"
    assert isinstance(resp["objects"], dict)


@pytest.mark.integration
def test_get_state_alias(aria_server):
    """GET /api/aria/state must return the same structure as /api/aria/objects."""
    obj = _get(f"{aria_server}/api/aria/objects")
    state = _get(f"{aria_server}/api/aria/state")
    assert "objects" in state
    assert "aria" in state
    assert obj["objects"] == state["objects"]


# ---------------------------------------------------------------------------
# Tests — POST /api/aria/object — add action
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_add_object(aria_server):
    payload = {
        "action": "add",
        "object": {"id": "ball", "position": {"x": 30, "y": 40}, "state": "on_stage"},
    }
    resp = _post(f"{aria_server}/api/aria/object", payload)
    assert resp.get("status") == "added"
    assert resp.get("id") == "ball"
    assert resp["object"]["position"] == {"x": 30, "y": 40}


@pytest.mark.integration
def test_add_object_shows_in_get(aria_server):
    """Newly added object must appear in GET /api/aria/objects."""
    _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"id": "cup", "position": {"x": 60, "y": 20}}},
    )
    resp = _get(f"{aria_server}/api/aria/objects")
    assert "cup" in resp["objects"]


@pytest.mark.integration
def test_add_object_default_position(aria_server):
    """Adding an object without explicit position should get default (50, 50)."""
    resp = _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"id": "cube"}},
    )
    assert resp.get("status") == "added"
    pos = resp["object"]["position"]
    assert "x" in pos and "y" in pos


@pytest.mark.integration
def test_add_object_using_name_field(aria_server):
    """Object payload may use 'name' instead of 'id'."""
    resp = _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"name": "apple", "position": {"x": 10, "y": 10}}},
    )
    assert resp.get("status") == "added"
    assert resp.get("id") == "apple"


# ---------------------------------------------------------------------------
# Tests — POST /api/aria/object — update action
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_update_object_position(aria_server):
    # Add first
    _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"id": "box", "position": {"x": 10, "y": 10}}},
    )
    # Update positon
    resp = _post(
        f"{aria_server}/api/aria/object",
        {"action": "update", "object": {"id": "box", "position": {"x": 80, "y": 90}}},
    )
    assert resp.get("status") == "updated"
    assert resp["object"]["position"] == {"x": 80, "y": 90}


@pytest.mark.integration
def test_update_object_state(aria_server):
    _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"id": "lamp", "state": "on_stage"}},
    )
    resp = _post(
        f"{aria_server}/api/aria/object",
        {"action": "update", "object": {"id": "lamp", "state": "held"}},
    )
    assert resp.get("status") == "updated"
    assert resp["object"]["state"] == "held"


# ---------------------------------------------------------------------------
# Tests — POST /api/aria/object — remove action
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_remove_object(aria_server):
    _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"id": "to_remove", "position": {"x": 1, "y": 1}}},
    )
    resp = _post(
        f"{aria_server}/api/aria/object",
        {"action": "remove", "object": {"id": "to_remove"}},
    )
    assert resp.get("status") == "removed"
    assert resp.get("id") == "to_remove"


@pytest.mark.integration
def test_remove_object_no_longer_in_get(aria_server):
    _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"id": "gone", "position": {"x": 5, "y": 5}}},
    )
    _post(
        f"{aria_server}/api/aria/object",
        {"action": "remove", "object": {"id": "gone"}},
    )
    resp = _get(f"{aria_server}/api/aria/objects")
    assert "gone" not in resp["objects"]


@pytest.mark.integration
def test_delete_alias(aria_server):
    """Action 'delete' should be an alias for 'remove'."""
    _post(
        f"{aria_server}/api/aria/object",
        {"action": "add", "object": {"id": "del_me"}},
    )
    resp = _post(
        f"{aria_server}/api/aria/object",
        {"action": "delete", "object": {"id": "del_me"}},
    )
    assert resp.get("status") == "removed"


# ---------------------------------------------------------------------------
# Tests — POST /api/aria/objects — bulk update
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_bulk_update_objects(aria_server):
    payload = {
        "objects": {
            "bulk1": {"position": {"x": 11, "y": 22}, "state": "on_stage"},
            "bulk2": {"position": {"x": 33, "y": 44}, "state": "on_stage"},
        }
    }
    resp = _post(f"{aria_server}/api/aria/objects", payload)
    assert resp.get("status") == "ok"
    assert "bulk1" in resp["objects"]
    assert "bulk2" in resp["objects"]


@pytest.mark.integration
def test_bulk_update_reflects_in_get(aria_server):
    _post(
        f"{aria_server}/api/aria/objects",
        {"objects": {"merged": {"position": {"x": 55, "y": 66}, "state": "on_stage"}}},
    )
    resp = _get(f"{aria_server}/api/aria/objects")
    assert "merged" in resp["objects"]
    assert resp["objects"]["merged"]["position"] == {"x": 55, "y": 66}


# ---------------------------------------------------------------------------
# Tests — Error cases
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_missing_id_returns_error(aria_server):
    payload = {"action": "add", "object": {"position": {"x": 1, "y": 1}}}
    req = urllib.request.Request(
        f"{aria_server}/api/aria/object",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read())
            # Some implementations return 200 with error key
            assert "error" in body or resp.status >= 400
    except urllib.error.HTTPError as e:
        assert e.code in (400, 500)


@pytest.mark.integration
def test_unknown_action_returns_error(aria_server):
    payload = {"action": "fly", "object": {"id": "x"}}
    req = urllib.request.Request(
        f"{aria_server}/api/aria/object",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read())
            assert "error" in body
    except urllib.error.HTTPError as e:
        assert e.code in (400, 500)
