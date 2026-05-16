"""
Aria Memory Store
Enables shared context across agents for autonomous planning and execution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import time
import sqlite3
import json
import threading
import os


class MemoryStore:
    def __init__(self, db_path: Optional[str] = None, autoload: bool = True):
        """In-memory event store with optional SQLite persistence.

        Args:
            db_path: optional path to SQLite DB file. If provided, events are
                persisted and loaded from disk.
            autoload: if True and db_path provided, load existing events into memory on init.
        """
        self.events: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        if db_path:
            parent = os.path.dirname(db_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            self._ensure_db()
            if autoload:
                self._load_from_db()

    def _ensure_db(self) -> None:
        if self._conn:
            return
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # use WAL for better concurrency
        try:
            self._conn.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, type TEXT, data TEXT)"
        )
        self._conn.commit()

    def _load_from_db(self) -> None:
        if not self._conn:
            return
        cur = self._conn.execute("SELECT timestamp, type, data FROM events ORDER BY id ASC")
        for ts, etype, data_text in cur.fetchall():
            try:
                data = json.loads(data_text) if data_text else {}
            except Exception:
                data = {"_raw": data_text}
            self.events.append({"timestamp": ts, "type": etype, "data": data})

    def write(self, event_type: str, data: Dict[str, Any]) -> None:
        with self._lock:
            event = {"timestamp": time.time(), "type": event_type, "data": dict(data)}
            self.events.append(event)
            if self._conn:
                try:
                    serialized = json.dumps(event["data"], ensure_ascii=False)
                except Exception:
                    serialized = json.dumps({"_repr": repr(event["data"])})
                self._conn.execute(
                    "INSERT INTO events (timestamp, type, data) VALUES (?, ?, ?)",
                    (event["timestamp"], event["type"], serialized),
                )
                self._conn.commit()

    def query(self, event_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        with self._lock:
            if self._conn:
                if event_type is None:
                    sql = "SELECT timestamp, type, data FROM events ORDER BY id ASC"
                    params = ()
                else:
                    sql = "SELECT timestamp, type, data FROM events WHERE type = ? ORDER BY id ASC"
                    params = (event_type,)
                cur = self._conn.execute(sql, params)
                rows = cur.fetchall()
                results = []
                for ts, etype, data_text in rows:
                    try:
                        data = json.loads(data_text) if data_text else {}
                    except Exception:
                        data = {"_raw": data_text}
                    results.append({"timestamp": ts, "type": etype, "data": data})
                if limit is not None:
                    return results[-limit:]
                return results
            # fallback to in-memory
            if event_type is None:
                results = list(self.events)
            else:
                results = [e for e in self.events if e["type"] == event_type]
            if limit is not None:
                return results[-limit:]
            return list(results)

    def last(self, n: int = 10) -> List[Dict[str, Any]]:
        return self.query(limit=n)

    def last_of_type(self, event_type: str) -> Optional[Dict[str, Any]]:
        matches = self.query(event_type=event_type, limit=1)
        return matches[-1] if matches else None

    def count_by_type(self) -> Dict[str, int]:
        with self._lock:
            if self._conn:
                cur = self._conn.execute("SELECT type, COUNT(1) FROM events GROUP BY type")
                return {row[0]: int(row[1]) for row in cur.fetchall()}
            counts: Dict[str, int] = {}
            for event in self.events:
                etype = event.get("type", "event")
                counts[etype] = counts.get(etype, 0) + 1
            return counts

    def clear(self) -> None:
        with self._lock:
            self.events.clear()
            if self._conn:
                self._conn.execute("DELETE FROM events")
                self._conn.commit()

    def close(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            finally:
                self._conn = None
