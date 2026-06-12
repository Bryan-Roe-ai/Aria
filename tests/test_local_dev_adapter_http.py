"""Integration-style tests for local_dev_adapter HTTP response builders.

These exercise the real ``function_app.ai_status`` handler through the adapter's
``get_ai_status_parts`` helper and the Flask app factory, validating the
``/api/ai/status`` contract surfaced by the local dev adapter.
"""

from __future__ import annotations

import json

import pytest

import local_dev_adapter as adapter


def test_get_ai_status_parts_returns_json_payload():
    body, status, mimetype, headers = adapter.get_ai_status_parts()

    assert status == 200
    assert isinstance(body, bytes)
    assert mimetype == "application/json"

    payload = json.loads(body.decode("utf-8"))
    # Health endpoint must report the active provider.
    assert "active_provider" in payload
    assert isinstance(headers, dict)


@pytest.mark.skipif(not adapter.HAS_FLASK, reason="Flask not installed")
def test_create_app_serves_ai_status_route():
    app = adapter.create_app()
    client = app.test_client()

    resp = client.get("/api/ai/status")

    assert resp.status_code == 200
    payload = json.loads(resp.get_data(as_text=True))
    assert "active_provider" in payload


@pytest.mark.skipif(not adapter.HAS_FLASK, reason="Flask not installed")
def test_create_app_unknown_route_404():
    app = adapter.create_app()
    client = app.test_client()

    resp = client.get("/api/does-not-exist")

    assert resp.status_code == 404
