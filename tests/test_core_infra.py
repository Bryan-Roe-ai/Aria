"""Tests for foundational core infrastructure modules.

Covers previously untested or under-tested modules:
- ``core.bus`` (AgentBus pub/sub)
- ``core.notifications`` (NotificationAdapter)
- ``core.memory.sqlite_backend`` (SQLiteMemoryBackend) and MemoryStore persistence
- ``core.ingestion.pipeline`` (FileDataSource, HttpDataSource, validator, pipeline)
"""

from __future__ import annotations

import json
from contextlib import contextmanager

import pytest

from core.bus import AgentBus
from core.ingestion.pipeline import (
    DataQualityValidator,
    DataSource,
    FileDataSource,
    HttpDataSource,
    IngestionPipeline,
)
from core.memory.sqlite_backend import SQLiteMemoryBackend
from core.memory.store import MemoryStore
from core.notifications import NotificationAdapter


# --------------------------------------------------------------------------- #
# AgentBus
# --------------------------------------------------------------------------- #
def test_bus_publish_delivers_to_all_subscribers():
    bus = AgentBus()
    received: list[dict] = []
    bus.subscribe("topic", lambda msg: received.append(msg))
    bus.subscribe("topic", lambda msg: msg.get("x", 0) * 2)

    results = bus.publish("topic", {"x": 5})

    assert received == [{"x": 5}]
    assert 10 in results
    assert len(results) == 2


def test_bus_publish_to_unknown_topic_returns_empty():
    bus = AgentBus()
    assert bus.publish("nobody", {"a": 1}) == []


def test_bus_publish_copies_message_per_subscriber():
    bus = AgentBus()

    def mutator(msg):
        msg["mutated"] = True
        return msg

    seen: list[dict] = []
    bus.subscribe("t", mutator)
    bus.subscribe("t", lambda msg: seen.append(dict(msg)))

    original = {"v": 1}
    bus.publish("t", original)

    # Original caller dict is untouched; second subscriber didn't see mutation.
    assert "mutated" not in original
    assert seen == [{"v": 1}]


def test_bus_unsubscribe_removes_callback_and_empty_topic():
    bus = AgentBus()
    calls: list[int] = []
    cb = lambda msg: calls.append(1)  # noqa: E731
    bus.subscribe("t", cb)
    bus.unsubscribe("t", cb)

    assert bus.publish("t", {}) == []
    # Topic dropped entirely when last subscriber removed.
    assert "t" not in bus._subscribers


def test_bus_unsubscribe_keeps_other_callbacks():
    bus = AgentBus()
    calls: list[str] = []
    keep = lambda msg: calls.append("keep")  # noqa: E731
    drop = lambda msg: calls.append("drop")  # noqa: E731
    bus.subscribe("t", keep)
    bus.subscribe("t", drop)
    bus.unsubscribe("t", drop)

    bus.publish("t", {})
    assert calls == ["keep"]


# --------------------------------------------------------------------------- #
# NotificationAdapter
# --------------------------------------------------------------------------- #
def test_notify_skipped_without_webhook():
    adapter = NotificationAdapter()
    result = adapter.notify("hello", {"k": "v"})
    assert result["status"] == "skipped"
    assert result["payload"]["message"] == "hello"
    assert result["payload"]["metadata"] == {"k": "v"}


def test_notify_defaults_metadata_to_empty_dict():
    adapter = NotificationAdapter()
    result = adapter.notify("hi")
    assert result["payload"]["metadata"] == {}


class _FakeResponse:
    def __init__(self, body: str, status: int = 200):
        self._body = body.encode("utf-8")
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_notify_sends_and_parses_json_response(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout=None):
        captured["data"] = request.data
        captured["timeout"] = timeout
        captured["url"] = request.full_url
        return _FakeResponse(json.dumps({"ok": True}), status=201)

    monkeypatch.setattr("core.notifications.urlopen", fake_urlopen)
    adapter = NotificationAdapter(webhook_url="https://example.test/hook", timeout=7)
    result = adapter.notify("event", {"n": 1})

    assert result["status"] == "sent"
    assert result["code"] == 201
    assert result["response"] == {"ok": True}
    assert captured["timeout"] == 7
    sent_payload = json.loads(captured["data"].decode("utf-8"))
    assert sent_payload == {"message": "event", "metadata": {"n": 1}}


def test_notify_returns_raw_body_when_not_json(monkeypatch):
    monkeypatch.setattr(
        "core.notifications.urlopen",
        lambda request, timeout=None: _FakeResponse("not-json"),
    )
    adapter = NotificationAdapter(webhook_url="https://example.test/hook")
    result = adapter.notify("event")
    assert result["status"] == "sent"
    assert result["response"] == "not-json"


def test_notify_empty_body_yields_none(monkeypatch):
    monkeypatch.setattr(
        "core.notifications.urlopen",
        lambda request, timeout=None: _FakeResponse(""),
    )
    adapter = NotificationAdapter(webhook_url="https://example.test/hook")
    result = adapter.notify("event")
    assert result["response"] is None


# --------------------------------------------------------------------------- #
# SQLiteMemoryBackend + MemoryStore persistence
# --------------------------------------------------------------------------- #
def _event(eid: str, epoch: float, etype: str = "t", data=None):
    return {
        "id": eid,
        "timestamp": f"2026-01-01T00:00:0{int(epoch)}+00:00",
        "epoch": epoch,
        "type": etype,
        "data": data or {"v": eid},
    }


def test_sqlite_backend_write_and_load_ordered_by_epoch(tmp_path):
    db = str(tmp_path / "events.db")
    backend = SQLiteMemoryBackend(db)
    backend.write(_event("b", 2.0))
    backend.write(_event("a", 1.0))
    backend.write(_event("c", 3.0))

    loaded = backend.load_all()
    assert [e["id"] for e in loaded] == ["a", "b", "c"]
    assert loaded[0]["data"] == {"v": "a"}


def test_sqlite_backend_insert_or_replace_dedupes(tmp_path):
    db = str(tmp_path / "events.db")
    backend = SQLiteMemoryBackend(db)
    backend.write(_event("x", 1.0, data={"v": "first"}))
    backend.write(_event("x", 1.0, data={"v": "second"}))

    loaded = backend.load_all()
    assert len(loaded) == 1
    assert loaded[0]["data"] == {"v": "second"}


def test_memory_store_persists_and_reloads(tmp_path):
    db = str(tmp_path / "store.db")
    store = MemoryStore(db_path=db)
    store.write("ingested", {"a": 1})
    store.write("ingested", {"a": 2})

    # New store instance loads persisted events from disk.
    reloaded = MemoryStore(db_path=db)
    events = reloaded.to_list()
    assert len(events) == 2
    assert [e["data"]["a"] for e in events] == [1, 2]


# --------------------------------------------------------------------------- #
# Ingestion pipeline
# --------------------------------------------------------------------------- #
def test_file_source_reads_json_array(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps([{"a": 1}, {"a": 2}]), encoding="utf-8")
    assert FileDataSource(str(path)).fetch() == [{"a": 1}, {"a": 2}]


def test_file_source_wraps_single_object(tmp_path):
    path = tmp_path / "obj.json"
    path.write_text(json.dumps({"a": 1}), encoding="utf-8")
    assert FileDataSource(str(path)).fetch() == [{"a": 1}]


def test_file_source_reads_jsonl(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text('{"a": 1}\n{"a": 2}\n', encoding="utf-8")
    assert FileDataSource(str(path)).fetch() == [{"a": 1}, {"a": 2}]


def test_file_source_reads_csv(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    rows = FileDataSource(str(path)).fetch()
    assert rows == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


def test_file_source_empty_returns_empty(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("   ", encoding="utf-8")
    assert FileDataSource(str(path)).fetch() == []


def test_validator_score_and_validate():
    v = DataQualityValidator()
    assert v.score({}) == 0.0
    assert v.score({"a": 1, "b": ""}) == 0.5
    assert v.validate({"a": 1, "b": 2}) is True
    assert v.validate({"a": 1, "b": ""}, min_score=0.6) is False


def test_validator_required_fields():
    v = DataQualityValidator().required_fields(["id"])
    assert v.validate({"id": 1, "x": 2}) is True
    assert v.validate({"x": 2}) is False


class _StubSource(DataSource):
    def __init__(self, records, raise_exc=False):
        self._records = records
        self._raise = raise_exc

    def fetch(self):
        if self._raise:
            raise RuntimeError("boom")
        return self._records


def test_pipeline_counts_ingested_and_rejected():
    memory = MemoryStore()
    validator = DataQualityValidator().required_fields(["id"])
    sources = [_StubSource([{"id": 1, "v": "a"}, {"v": "no-id"}])]
    pipeline = IngestionPipeline(sources, memory, validator)

    result = pipeline.run()
    assert result == {"ingested": 1, "rejected": 1}
    assert len(memory.to_list()) == 1


def test_pipeline_skips_failing_source():
    memory = MemoryStore()
    sources = [_StubSource([], raise_exc=True), _StubSource([{"id": 1}])]
    pipeline = IngestionPipeline(sources, memory)
    result = pipeline.run()
    assert result == {"ingested": 1, "rejected": 0}


def test_pipeline_without_validator_ingests_all():
    memory = MemoryStore()
    pipeline = IngestionPipeline([_StubSource([{"a": 1}, {"b": 2}])], memory)
    assert pipeline.run() == {"ingested": 2, "rejected": 0}


def test_http_source_fetch_wraps_object(monkeypatch):
    @contextmanager
    def fake_urlopen(request, timeout=None):
        yield _FakeResponse(json.dumps({"a": 1}))

    monkeypatch.setattr("core.ingestion.pipeline.urlopen", fake_urlopen)
    assert HttpDataSource("https://x.test").fetch() == [{"a": 1}]


def test_http_source_fetch_returns_list(monkeypatch):
    @contextmanager
    def fake_urlopen(request, timeout=None):
        yield _FakeResponse(json.dumps([{"a": 1}, {"a": 2}]))

    monkeypatch.setattr("core.ingestion.pipeline.urlopen", fake_urlopen)
    assert HttpDataSource("https://x.test").fetch() == [{"a": 1}, {"a": 2}]


def test_datasource_is_abstract():
    with pytest.raises(TypeError):
        DataSource()  # type: ignore[abstract]
