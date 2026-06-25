from __future__ import annotations

import copy
import json
import os
import threading
from pathlib import Path
from typing import Any


def _default_stage_state_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    configured = os.getenv("ARIA_STAGE_STATE_PATH")
    if configured:
        return Path(configured).expanduser()
    return repo_root / "data_out" / "aria" / "stage_state.json"


def _unwrap(value: Any) -> Any:
    if isinstance(value, PersistentDict):
        return {key: _unwrap(item) for key, item in value.items()}
    if isinstance(value, PersistentList):
        return [_unwrap(item) for item in value]
    return copy.deepcopy(value)


class PersistentDict(dict):
    def __init__(self, store: "StageStateStore", initial: dict[str, Any] | None = None) -> None:
        super().__init__()
        self._store = store
        for key, value in (initial or {}).items():
            super().__setitem__(key, store._wrap(value))

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(key, self._store._wrap(value))
        self._store.persist()

    def __delitem__(self, key: str) -> None:
        super().__delitem__(key)
        self._store.persist()

    def clear(self) -> None:
        super().clear()
        self._store.persist()

    def pop(self, key: str, default: Any = None) -> Any:
        if key in self:
            result = super().pop(key)
            self._store.persist()
            return result
        return default

    def popitem(self) -> tuple[str, Any]:
        item = super().popitem()
        self._store.persist()
        return item

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key in self:
            return self[key]
        self[key] = default
        return self[key]

    def update(self, other: dict[str, Any] | None = None, **kwargs: Any) -> None:
        payload: dict[str, Any] = {}
        if other:
            payload.update(dict(other))
        if kwargs:
            payload.update(kwargs)
        for key, value in payload.items():
            super().__setitem__(key, self._store._wrap(value))
        if payload:
            self._store.persist()


class PersistentList(list):
    def __init__(self, store: "StageStateStore", initial: list[Any] | None = None) -> None:
        super().__init__(store._wrap(item) for item in (initial or []))
        self._store = store

    def __setitem__(self, index, value):  # type: ignore[override]
        if isinstance(index, slice):
            value = [self._store._wrap(item) for item in value]
        else:
            value = self._store._wrap(value)
        super().__setitem__(index, value)
        self._store.persist()

    def __delitem__(self, index):  # type: ignore[override]
        super().__delitem__(index)
        self._store.persist()

    def append(self, value: Any) -> None:
        super().append(self._store._wrap(value))
        self._store.persist()

    def clear(self) -> None:
        super().clear()
        self._store.persist()

    def extend(self, values) -> None:
        super().extend(self._store._wrap(value) for value in values)
        self._store.persist()

    def insert(self, index: int, value: Any) -> None:
        super().insert(index, self._store._wrap(value))
        self._store.persist()

    def pop(self, index: int = -1):  # type: ignore[override]
        value = super().pop(index)
        self._store.persist()
        return value

    def remove(self, value: Any) -> None:
        super().remove(value)
        self._store.persist()


class StageStateStore:
    def __init__(self, default_state: dict[str, Any], *, path: Path | None = None) -> None:
        self._lock = threading.RLock()
        self._path = path or _default_stage_state_path()
        self._default_state = copy.deepcopy(default_state)
        self.state = self._wrap(self._load_initial_state())

    def _load_initial_state(self) -> dict[str, Any]:
        try:
            if self._path.exists():
                loaded = json.loads(self._path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    return loaded
        except Exception:
            pass
        return copy.deepcopy(self._default_state)

    def _wrap(self, value: Any) -> Any:
        if isinstance(value, PersistentDict | PersistentList):
            return value
        if isinstance(value, dict):
            return PersistentDict(self, value)
        if isinstance(value, list):
            return PersistentList(self, value)
        return copy.deepcopy(value)

    def persist(self) -> None:
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = _unwrap(self.state)
            tmp_path = self._path.with_suffix(f"{self._path.suffix}.tmp")
            tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp_path.replace(self._path)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return _unwrap(self.state)

    def replace(self, new_state: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self.state.clear()
            self.state.update(copy.deepcopy(new_state))
            self.persist()
            return self.state

    def merge(self, patch: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self.state.update(copy.deepcopy(patch))
            self.persist()
            return self.state

    def reset(self) -> dict[str, Any]:
        return self.replace(self._default_state)
