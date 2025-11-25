"""Generic lightweight SQL repository utilities.

Provides a key-value store abstraction for multi-database support using
SQLAlchemy core. Table auto-creation is vendor-aware and idempotent.

Table name: QAI_KeyValue
Columns:
  k (primary key), v (text/blob), updated_at (timestamp)

Graceful degradation: if engine unavailable operations return fallback values
instead of raising.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import text  # type: ignore
from .sql_engine import get_engine

_TABLE_CREATED = False

# ----------------------------------------------------------------------------
# Table Creation (idempotent)
# ----------------------------------------------------------------------------

def _ensure_table():
    global _TABLE_CREATED
    if _TABLE_CREATED:
        return True
    engine = get_engine()
    if not engine:
        return False
    vendor = getattr(engine.dialect, "name", "unknown")
    try:
        if vendor == "sqlite":
            ddl = "CREATE TABLE IF NOT EXISTS QAI_KeyValue (k TEXT PRIMARY KEY, v TEXT, updated_at TEXT)"
        elif vendor in {"postgresql", "postgres"}:
            ddl = (
                "CREATE TABLE IF NOT EXISTS QAI_KeyValue ("
                "k VARCHAR(200) PRIMARY KEY, "
                "v TEXT, "
                "updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)"
            )
        elif vendor in {"mysql"}:
            ddl = (
                "CREATE TABLE IF NOT EXISTS QAI_KeyValue ("
                "k VARCHAR(200) PRIMARY KEY, "
                "v TEXT, "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)"
            )
        else:  # mssql & fallback
            # SQL Server: need IF NOT EXISTS pattern
            ddl = (
                "IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='QAI_KeyValue') "
                "BEGIN CREATE TABLE dbo.QAI_KeyValue ("
                "k NVARCHAR(200) NOT NULL PRIMARY KEY, "
                "v NVARCHAR(MAX) NULL, "
                "updated_at DATETIME2 DEFAULT SYSUTCDATETIME()) END"
            )
        with engine.begin() as conn:
            conn.execute(text(ddl))
        _TABLE_CREATED = True
        return True
    except Exception as e:  # noqa: BLE001
        logging.warning(f"[sql_repository] table create failed: {e}")
        return False

# ----------------------------------------------------------------------------
# CRUD Operations
# ----------------------------------------------------------------------------

def put_value(key: str, value: str) -> bool:
    if not _ensure_table():
        return False
    engine = get_engine()
    if not engine:
        return False
    vendor = getattr(engine.dialect, "name", "unknown")
    try:
        with engine.begin() as conn:
            if vendor == "sqlite":
                conn.execute(text("REPLACE INTO QAI_KeyValue (k,v,updated_at) VALUES (:k,:v,:ts)"), {"k": key, "v": value, "ts": datetime.utcnow().isoformat()})
            elif vendor in {"postgresql", "postgres"}:
                conn.execute(text("INSERT INTO QAI_KeyValue (k,v) VALUES (:k,:v) ON CONFLICT (k) DO UPDATE SET v=EXCLUDED.v, updated_at=CURRENT_TIMESTAMP"), {"k": key, "v": value})
            elif vendor == "mysql":
                conn.execute(text("INSERT INTO QAI_KeyValue (k,v) VALUES (:k,:v) ON DUPLICATE KEY UPDATE v=VALUES(v)"), {"k": key, "v": value})
            else:  # SQL Server
                conn.execute(text("MERGE dbo.QAI_KeyValue AS tgt USING (SELECT :k AS k, :v AS v) AS src ON tgt.k=src.k WHEN MATCHED THEN UPDATE SET v=src.v, updated_at=SYSUTCDATETIME() WHEN NOT MATCHED THEN INSERT (k,v,updated_at) VALUES (src.k, src.v, SYSUTCDATETIME());"), {"k": key, "v": value})
        return True
    except Exception as e:  # noqa: BLE001
        logging.warning(f"[sql_repository] put_value failed: {e}")
        return False


def get_value(key: str) -> Optional[str]:
    if not _ensure_table():
        return None
    engine = get_engine()
    if not engine:
        return None
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT v FROM QAI_KeyValue WHERE k=:k"), {"k": key}).fetchone()
            return None if not res else res[0]
    except Exception as e:  # noqa: BLE001
        logging.warning(f"[sql_repository] get_value failed: {e}")
        return None


def delete_value(key: str) -> bool:
    if not _ensure_table():
        return False
    engine = get_engine()
    if not engine:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM QAI_KeyValue WHERE k=:k"), {"k": key})
        return True
    except Exception as e:  # noqa: BLE001
        logging.warning(f"[sql_repository] delete_value failed: {e}")
        return False


def list_values(limit: int = 100) -> list[dict]:  # noqa: ANN001
    if not _ensure_table():
        return []
    engine = get_engine()
    if not engine:
        return []
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT k, v, updated_at FROM QAI_KeyValue ORDER BY updated_at DESC"))
            items = []
            for row in res.fetchall()[:limit]:
                items.append({"k": row[0], "v": row[1], "updated_at": row[2]})
            return items
    except Exception as e:  # noqa: BLE001
        logging.warning(f"[sql_repository] list_values failed: {e}")
        return []

__all__ = ["put_value", "get_value", "delete_value", "list_values"]
