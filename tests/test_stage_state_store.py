from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).parent.parent / "apps" / "aria" / "stage_state_store.py"
MODULE_SPEC = importlib.util.spec_from_file_location("aria_stage_state_store_under_test", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
stage_state_store = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = stage_state_store
MODULE_SPEC.loader.exec_module(stage_state_store)


def test_stage_state_store_persists_nested_mutations(tmp_path: Path) -> None:
    path = tmp_path / "stage_state.json"
    default_state = {
        "aria": {"held_object": None},
        "objects": {"cup": {"position": {"x": 10, "y": 20}}},
        "history": [],
    }

    store = stage_state_store.StageStateStore(default_state, path=path)
    store.state["aria"]["held_object"] = "cup"
    store.state["objects"]["cup"]["position"]["x"] = 42
    store.state["history"].append({"action": "pickup", "object_id": "cup"})

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["aria"]["held_object"] == "cup"
    assert payload["objects"]["cup"]["position"]["x"] == 42
    assert payload["history"] == [{"action": "pickup", "object_id": "cup"}]


def test_stage_state_store_reloads_persisted_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "stage_state.json"
    default_state = {"aria": {"held_object": None}, "objects": {}, "history": []}

    first = stage_state_store.StageStateStore(default_state, path=path)
    first.state["aria"]["held_object"] = "book"

    second = stage_state_store.StageStateStore(default_state, path=path)
    assert second.snapshot()["aria"]["held_object"] == "book"
