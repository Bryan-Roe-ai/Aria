"""Unit tests for mount.app health/status endpoints and request middleware."""

from __future__ import annotations

import importlib
from datetime import datetime, timezone

from fastapi.testclient import TestClient


class _IntegrationOK:
    async def get_status(self):
        return {"component": "ok"}


class _IntegrationFail:
    async def get_status(self):
        raise RuntimeError("boom")


class _IntegrationSlow:
    async def get_status(self):
        # Keep deterministic without real sleep; readiness/status timeout logic
        # itself is unit-covered via monkeypatched timeout constant where needed.
        return {"component": "slow-but-ok"}


def _load_app_module():
    return importlib.import_module("mount.app")


def test_health_and_liveness_include_expected_fields(monkeypatch):
    mod = _load_app_module()

    # Stabilize uptime expectations by ensuring startup_time is not in future.
    monkeypatch.setattr(mod, "startup_time_utc", datetime.now(timezone.utc))

    client = TestClient(mod.app)

    health = client.get("/health")
    assert health.status_code == 200
    payload = health.json()
    assert payload["status"] == "healthy"
    assert "timestamp" in payload
    assert "startup_time" in payload
    assert isinstance(payload["uptime_seconds"], int)
    assert payload["uptime_seconds"] >= 0

    live = client.get("/health/live")
    assert live.status_code == 200
    assert live.json()["status"] == "alive"


def test_request_id_header_is_generated_and_echoed(monkeypatch):
    mod = _load_app_module()
    client = TestClient(mod.app)

    generated = client.get("/health")
    assert generated.status_code == 200
    assert generated.headers.get("x-request-id")
    assert generated.headers.get("x-process-time-ms")

    supplied = client.get("/health", headers={"x-request-id": "req-123"})
    assert supplied.status_code == 200
    assert supplied.headers.get("x-request-id") == "req-123"


def test_readiness_returns_503_when_any_component_fails(monkeypatch):
    mod = _load_app_module()
    monkeypatch.setattr(mod, "quantum_integration", _IntegrationOK())
    monkeypatch.setattr(mod, "chat_integration", _IntegrationFail())
    monkeypatch.setattr(mod, "training_integration", _IntegrationOK())

    client = TestClient(mod.app)
    resp = client.get("/health/ready")

    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["quantum"] == "ok"
    assert body["checks"]["training"] == "ok"
    assert body["checks"]["chat"].startswith("error:")


def test_status_remains_200_and_reports_degraded_with_partial_failures(monkeypatch):
    mod = _load_app_module()
    monkeypatch.setattr(mod, "quantum_integration", _IntegrationOK())
    monkeypatch.setattr(mod, "chat_integration", _IntegrationFail())
    monkeypatch.setattr(mod, "training_integration", _IntegrationSlow())

    client = TestClient(mod.app)
    resp = client.get("/status")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["quantum"] == "ok"
    assert body["checks"]["training"] == "ok"
    assert body["checks"]["chat"].startswith("error:")

    # Payloads should still include successful components while failed is null.
    assert body["quantum"] == {"component": "ok"}
    assert body["training"] == {"component": "slow-but-ok"}
    assert body["chat"] is None


def test_status_reports_healthy_when_all_components_ok(monkeypatch):
    mod = _load_app_module()
    monkeypatch.setattr(mod, "quantum_integration", _IntegrationOK())
    monkeypatch.setattr(mod, "chat_integration", _IntegrationOK())
    monkeypatch.setattr(mod, "training_integration", _IntegrationOK())

    client = TestClient(mod.app)
    resp = client.get("/status")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["checks"] == {
        "quantum": "ok",
        "chat": "ok",
        "training": "ok",
    }
