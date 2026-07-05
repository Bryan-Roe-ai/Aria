"""Local SQL tooling helpers for Aria development.

Usage examples:
  python scripts/sql_local_tools.py setup
  python scripts/sql_local_tools.py status
  python scripts/sql_local_tools.py reset
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_SQL_URL = "sqlite:///data_out/qai_local.db"
DEFAULT_DB_PATH = Path("data_out/qai_local.db")
CHECK_TABLE_DDL = "CREATE TABLE IF NOT EXISTS sql_setup_check (id INTEGER PRIMARY KEY, note TEXT NOT NULL)"
CHECK_INSERT_SQL = "INSERT INTO sql_setup_check (note) VALUES ('sql configured')"
CHECK_COUNT_SQL = "SELECT COUNT(*) FROM sql_setup_check"
ENGINE_UNAVAILABLE_MSG = "SQL engine not available. Ensure dependencies are installed."


def _sql_api() -> tuple[Callable[[], Any], Callable[[], dict[str, Any]]]:
    from shared.sql_engine import get_engine, sql_health

    return get_engine, sql_health


def _clear_cached_engine() -> None:
    import shared.sql_engine as eng

    engine = getattr(eng, "_ENGINE", None)
    if engine is not None:
        try:
            dispose = getattr(engine, "dispose", None)
            if callable(dispose):
                dispose()
        except Exception:
            pass
    eng._ENGINE = None
    eng._LAST_URL = None


def _effective_url(url: str | None) -> str:
    return (url or os.getenv("QAI_SQL_URL") or DEFAULT_SQL_URL).strip()


def _ensure_bootstrap_row() -> None:
    get_engine, _ = _sql_api()
    engine = get_engine()
    if engine is None:
        raise RuntimeError(ENGINE_UNAVAILABLE_MSG)
    engine = cast(Any, engine)

    with engine.begin() as conn:
        conn.execute(text(CHECK_TABLE_DDL))
        conn.execute(text(CHECK_INSERT_SQL))


def _status_row_count() -> int:
    get_engine, _ = _sql_api()
    engine = get_engine()
    if engine is None:
        raise RuntimeError(ENGINE_UNAVAILABLE_MSG)
    engine = cast(Any, engine)

    with engine.connect() as conn:
        conn.execute(text(CHECK_TABLE_DDL))
        result = conn.execute(text(CHECK_COUNT_SQL)).scalar_one()
        return int(result)


def cmd_setup() -> None:
    _, sql_health = _sql_api()
    Path("data_out").mkdir(parents=True, exist_ok=True)
    _ensure_bootstrap_row()
    print("sql_health=", sql_health())
    configured_url = os.environ.get("QAI_SQL_URL", DEFAULT_SQL_URL)
    print(f"✅ Local SQL bootstrap complete. Set QAI_SQL_URL={configured_url}")


def cmd_status(json_output: bool = False) -> None:
    _, sql_health = _sql_api()
    health = sql_health()
    row_count = _status_row_count()
    if json_output:
        print(
            json.dumps(
                {
                    "sql_health": health,
                    "sql_setup_check_rows": row_count,
                }
            )
        )
        return
    print("sql_health=", health)
    print("sql_setup_check_rows=", row_count)


def cmd_doctor(json_output: bool = False) -> int:
    _, sql_health = _sql_api()
    health = sql_health()
    ok = bool(health.get("enabled")) and bool(health.get("connectivity"))
    payload = {
        "ok": ok,
        "sql_health": health,
    }
    if json_output:
        print(json.dumps(payload))
    else:
        if ok:
            print("✅ SQL doctor: healthy")
        else:
            print("❌ SQL doctor: unhealthy")
        print("sql_health=", health)
    return 0 if ok else 1


def cmd_reset(db_path: Path) -> None:
    print(f"♻️  Resetting local SQLite database at {db_path}...")
    _clear_cached_engine()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    cmd_setup()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local SQL helper commands for Aria")
    parser.add_argument(
        "command",
        choices=["setup", "status", "reset", "doctor"],
        help="Command to run",
    )
    parser.add_argument(
        "--url",
        default=None,
        help=(f"SQL URL override (default: env QAI_SQL_URL or {DEFAULT_SQL_URL})"),
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help=(f"Path to local SQLite DB file for reset (default: {DEFAULT_DB_PATH})"),
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Emit status output in JSON format",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.environ["QAI_SQL_URL"] = _effective_url(args.url)

    if args.command == "setup":
        cmd_setup()
    elif args.command == "status":
        cmd_status(json_output=args.json_output)
    elif args.command == "reset":
        cmd_reset(Path(args.db_path))
    elif args.command == "doctor":
        return cmd_doctor(json_output=args.json_output)
    else:
        raise ValueError(f"Unsupported command: {args.command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
