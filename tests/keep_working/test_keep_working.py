"""Tests for Keep Working Pomodoro timer and persistence."""

import json
import sys
from pathlib import Path

# Ensure the launcher is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from notebooks.keep_working_launcher import (
    DEFAULT_SETTINGS,
    SessionRecord,
    append_json_record,
    export_systemd,
    load_config,
    save_config,
    update_status_file,
)


def test_session_record_fields():
    rec = SessionRecord(task_name="t", start_ts="a", end_ts="b", duration_s=10, kind="work")
    assert rec.task_name == "t"
    assert rec.kind == "work"
    assert rec.duration_s == 10


def test_persistence_write(tmp_path):
    p = tmp_path / "hist.json"
    rec = SessionRecord(task_name="t", start_ts="a", end_ts="b", duration_s=10, kind="work")
    append_json_record(rec, path=p)
    assert p.exists()
    data = json.loads(p.read_text())
    assert len(data) == 1
    assert data[0]["task_name"] == "t"


def test_persistence_append(tmp_path):
    p = tmp_path / "hist.json"
    rec1 = SessionRecord(task_name="t1", start_ts="a", end_ts="b", duration_s=10, kind="work")
    rec2 = SessionRecord(task_name="t2", start_ts="c", end_ts="d", duration_s=20, kind="short_break")
    append_json_record(rec1, path=p)
    append_json_record(rec2, path=p)
    data = json.loads(p.read_text())
    assert len(data) == 2
    assert data[1]["task_name"] == "t2"


def test_save_config_strips_unknown_keys(tmp_path):
    p = tmp_path / "cfg.json"
    cleaned = save_config({"task": "X", "work": 10, "bogus": 1}, path=p)
    assert cleaned["task"] == "X"
    assert cleaned["work"] == 10
    assert "bogus" not in cleaned
    assert set(cleaned) == set(DEFAULT_SETTINGS)


def test_load_config_roundtrip(tmp_path):
    p = tmp_path / "cfg.json"
    save_config({"task": "Roundtrip", "short": 7}, path=p)
    loaded = load_config(path=p)
    assert loaded["task"] == "Roundtrip"
    assert loaded["short"] == 7


def test_load_config_missing_returns_defaults(tmp_path):
    loaded = load_config(path=tmp_path / "absent.json")
    assert loaded == DEFAULT_SETTINGS
    assert loaded is not DEFAULT_SETTINGS  # must be a copy


def test_load_config_corrupt_returns_defaults(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json")
    assert load_config(path=p)["task"] == DEFAULT_SETTINGS["task"]


def test_export_systemd_includes_flags(tmp_path):
    svc = export_systemd(tmp_path / "k.service", task="Deep", work=5, notify=True, sound=True, repeat=True)
    text = Path(svc).read_text()
    assert "ExecStart=" in text
    assert "--notify" in text
    assert "--sound" in text
    assert "--repeat" in text
    assert "WantedBy=default.target" in text


def test_export_systemd_omits_unset_flags(tmp_path):
    svc = export_systemd(tmp_path / "k.service", task="Plain", work=5)
    text = Path(svc).read_text()
    assert "--notify" not in text
    assert "--repeat" not in text


def test_update_status_file(tmp_path):
    p = tmp_path / "status.json"
    rec = SessionRecord(task_name="t", start_ts="a", end_ts="b", duration_s=3, kind="work")
    update_status_file(p, rec=rec, cycle_count=2, running=True)
    data = json.loads(p.read_text())
    assert data["cycle_count"] == 2
    assert data["running"] is True
    assert data["last_session"]["task_name"] == "t"
    assert "updated_at" in data


def test_update_status_file_running_no_record(tmp_path):
    p = tmp_path / "status.json"
    update_status_file(p, rec=None, cycle_count=1, running=True)
    data = json.loads(p.read_text())
    assert data["last_session"] is None
    assert data["running"] is True
