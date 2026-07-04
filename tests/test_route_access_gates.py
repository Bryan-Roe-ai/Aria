from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _mock_request(
    method: str = "GET",
    body: dict | None = None,
    params: dict | None = None,
    headers: dict | None = None,
) -> MagicMock:
    req = MagicMock()
    req.method = method
    req.params = params or {}
    req.route_params = {}
    req.headers = headers or {}

    if body is not None:
        raw = json.dumps(body).encode("utf-8")
        req.get_json.return_value = body
        req.get_body.return_value = raw
    else:
        req.get_json.side_effect = ValueError("No JSON body")
        req.get_body.return_value = b""

    return req


@pytest.fixture(scope="module")
def app_module():
    try:
        import function_app

        return function_app
    except Exception as exc:
        pytest.skip(f"Cannot import function_app: {exc}")


def test_subscription_status_requires_token_when_global_protection_enabled(monkeypatch, app_module):
    monkeypatch.setenv("QAI_PROTECT_RISKY_ROUTES", "1")
    monkeypatch.setenv("QAI_ROUTE_ACCESS_TOKEN", "secret123")
    monkeypatch.setattr(app_module, "subscription_manager_available", False)

    resp = app_module.subscription_status(_mock_request("GET"))

    assert resp.status_code == 401
    payload = json.loads(resp.get_body())
    assert payload["scope"] == "subscriptions"


def test_subscription_status_allows_token_when_global_protection_enabled(monkeypatch, app_module):
    monkeypatch.setenv("QAI_PROTECT_RISKY_ROUTES", "1")
    monkeypatch.setenv("QAI_ROUTE_ACCESS_TOKEN", "secret123")
    monkeypatch.setattr(app_module, "subscription_manager_available", False)

    resp = app_module.subscription_status(_mock_request("GET", headers={"X-QAI-ACCESS-TOKEN": "secret123"}))

    assert resp.status_code == 503


def test_subscription_pricing_remains_public(monkeypatch, app_module):
    monkeypatch.setenv("QAI_PROTECT_RISKY_ROUTES", "1")
    monkeypatch.setenv("QAI_ROUTE_ACCESS_TOKEN", "secret123")

    resp = app_module.subscription_pricing(_mock_request("GET"))

    assert resp.status_code == 200


def test_aria_command_accepts_platform_principal_when_auth_required(monkeypatch, app_module):
    monkeypatch.setenv("QAI_REQUIRE_AUTH_FOR_ARIA", "1")
    monkeypatch.setattr(
        app_module,
        "_proxy_aria_request",
        lambda req, subpath: app_module.func.HttpResponse(
            json.dumps({"status": "ok", "subpath": subpath}),
            status_code=200,
            mimetype="application/json",
            headers=app_module.create_cors_response_headers(),
        ),
    )

    resp = app_module.aria_command_proxy(
        _mock_request("POST", body={"command": "wave"}, headers={"X-Forwarded-User": "user@example.com"})
    )

    assert resp.status_code == 200
    payload = json.loads(resp.get_body())
    assert payload["subpath"] == "command"
