"""Tests for shared/agi_backend_status.py."""

from shared.agi_backend_status import build_agi_backend_status


class _FakeProvider:
    def __init__(self, persistence=None, context=None):
        self.persistence = persistence
        self.context = context


def test_backend_status_none(monkeypatch):
    for key in (
        "QAI_AGI_PERSIST",
        "QAI_AGI_PERSIST_PATH",
        "QAI_AGI_PERSIST_DB",
        "QAI_AGI_PERSIST_SQLITE",
        "QAI_AGI_MEMORY_BACKEND",
        "QAI_AGI_REDIS_URL",
        "REDIS_URL",
        "QAI_AGI_PERSIST_READ_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)

    status = build_agi_backend_status()
    assert status["persistence"]["type"] == "none"
    assert status["persistence"]["attached"] is False
    assert status["memory"]["type"] == "in_process"


def test_backend_status_jsonl(monkeypatch, tmp_path):
    path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("QAI_AGI_PERSIST", "1")
    monkeypatch.setenv("QAI_AGI_PERSIST_PATH", str(path))
    monkeypatch.setenv("QAI_AGI_PERSIST_READ_TOKEN", "secret")

    provider = _FakeProvider(persistence=object())
    status = build_agi_backend_status(provider)
    assert status["persistence"]["type"] == "jsonl"
    assert status["persistence"]["attached"] is True
    assert status["persistence"]["read_token_configured"] is True


def test_backend_status_sqlite(monkeypatch, tmp_path):
    db = tmp_path / "agi.db"
    monkeypatch.setenv("QAI_AGI_PERSIST_DB", str(db))

    status = build_agi_backend_status()
    assert status["persistence"]["type"] == "sqlite"
    assert status["persistence"]["sqlite_path"] == str(db)


def test_backend_status_redis_env(monkeypatch):
    monkeypatch.setenv("QAI_AGI_MEMORY_BACKEND", "redis")
    monkeypatch.setenv("QAI_AGI_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("QAI_AGI_SESSION_ID", "test-session")

    class RedisAGIMemoryStub:
        pass

    provider = _FakeProvider(context=RedisAGIMemoryStub())
    status = build_agi_backend_status(provider)
    assert status["memory"]["type"] == "redis"
    assert status["memory"]["backend_env"] == "redis"
    assert status["memory"]["redis_url_configured"] is True
    assert status["memory"]["session_id"] == "test-session"
