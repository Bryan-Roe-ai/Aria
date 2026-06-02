"""Focused tests for the core notification adapter."""

from __future__ import annotations

from urllib.error import URLError

from core.notifications import NotificationAdapter


def test_notification_adapter_skips_without_webhook_url() -> None:
    adapter = NotificationAdapter()

    result = adapter.notify("cycle complete", {"ok": True})

    assert result["status"] == "skipped"
    assert result["payload"] == {
        "message": "cycle complete",
        "metadata": {"ok": True},
    }


def test_notification_adapter_returns_failure_on_network_error(
    monkeypatch,
) -> None:
    def fake_urlopen(*args, **kwargs):
        raise URLError("boom")

    monkeypatch.setattr("core.notifications.urlopen", fake_urlopen)

    adapter = NotificationAdapter("http://example.invalid")
    result = adapter.notify("cycle complete")

    assert result["status"] == "failed"
    assert result["payload"] == {
        "message": "cycle complete",
        "metadata": {},
    }
    assert "boom" in result["error"]


def test_notification_adapter_preserves_non_json_response(monkeypatch) -> None:
    class _Response:
        status = 204

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"ok-but-not-json"

    def fake_urlopen(*args, **kwargs):
        return _Response()

    monkeypatch.setattr("core.notifications.urlopen", fake_urlopen)

    adapter = NotificationAdapter("http://example.invalid")
    result = adapter.notify("cycle complete")

    assert result["status"] == "sent"
    assert result["code"] == 204
    assert result["response"] == "ok-but-not-json"
