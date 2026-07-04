"""Tests for data_out status JSON repair utility."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.repair_data_out_status import (  # noqa: E402
    cleanup_json_text,
    repair_all,
    repair_status_file,
    resolve_merge_conflicts,
)


def test_resolve_merge_conflicts_keeps_head_section():
    text = (
        "{\n"
        '  "value": "old",\n'
        "<<<<<<< HEAD\n"
        '  "winner": "head",\n'
        "=======\n"
        '  "winner": "other",\n'
        ">>>>>>> Stashed changes\n"
        "}\n"
    )

    resolved, rounds = resolve_merge_conflicts(text)
    resolved = cleanup_json_text(resolved)

    assert rounds == 1
    payload = json.loads(resolved)
    assert payload["winner"] == "head"


def test_resolve_merge_conflicts_handles_nested_blocks():
    text = (
        "{\n"
        "<<<<<<< HEAD\n"
        '  "task_id": "head",\n'
        "=======\n"
        "<<<<<<< Updated upstream\n"
        '  "task_id": "upstream",\n'
        "=======\n"
        '  "task_id": "stashed",\n'
        ">>>>>>> Stashed changes\n"
        ">>>>>>> outer\n"
        "}\n"
    )

    resolved, rounds = resolve_merge_conflicts(text)
    resolved = cleanup_json_text(resolved)

    assert rounds >= 1
    payload = json.loads(resolved)
    assert payload["task_id"] == "head"


def test_repair_status_file_writes_valid_json(tmp_path):
    path = tmp_path / "sample" / "status.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        '{\n<<<<<<< HEAD\n  "last_updated": "2026-06-01T00:00:00+00:00"\n=======\n  "last_updated": "2025-01-01T00:00:00+00:00"\n>>>>>>> other\n}\n',
        encoding="utf-8",
    )

    result = repair_status_file(path)

    assert result["status"] == "repaired"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["last_updated"] == "2026-06-01T00:00:00+00:00"


def test_refresh_stale_updates_timestamp(tmp_path):
    stale = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    path = tmp_path / "stale" / "status.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"last_updated": stale}), encoding="utf-8")

    result = repair_status_file(path, refresh_stale=True)

    assert result["status"] == "repaired"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["last_updated"] != stale


def test_repair_all_skips_agent_output(tmp_path):
    data_dir = tmp_path / "data_out"
    orchestrator = data_dir / "orchestrator" / "status.json"
    agent = data_dir / "agents" / "self" / "status.json"
    orchestrator.parent.mkdir(parents=True)
    agent.parent.mkdir(parents=True)
    orchestrator.write_text(
        '{\n<<<<<<< HEAD\n  "ok": true\n=======\n  "ok": false\n>>>>>>> other\n}\n', encoding="utf-8"
    )
    agent.write_text('{\n<<<<<<< HEAD\n  "ok": true\n=======\n  "ok": false\n>>>>>>> other\n}\n', encoding="utf-8")

    results = repair_all(data_dir)

    assert len(results) == 1
    assert json.loads(orchestrator.read_text(encoding="utf-8"))["ok"] is True
    assert "<<<<<<<" in agent.read_text(encoding="utf-8")
