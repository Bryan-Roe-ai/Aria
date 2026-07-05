from __future__ import annotations

import os
import sys
import json
from typing import Any
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

pytestmark = pytest.mark.unit


def _tools() -> Any:
    import scripts.sql_local_tools as tools

    return tools


@pytest.fixture(autouse=True)
def _reset_sql_engine_state():
    import shared.sql_engine as eng

    eng._ENGINE = None
    eng._LAST_URL = None
    old_url = os.environ.get("QAI_SQL_URL")
    yield
    eng._ENGINE = None
    eng._LAST_URL = None
    if old_url is None:
        os.environ.pop("QAI_SQL_URL", None)
    else:
        os.environ["QAI_SQL_URL"] = old_url


def test_effective_url_precedence(monkeypatch: pytest.MonkeyPatch):
    tools = _tools()
    monkeypatch.setenv("QAI_SQL_URL", "sqlite:///env.db")
    assert tools._effective_url(None) == "sqlite:///env.db"
    assert tools._effective_url("sqlite:///arg.db") == "sqlite:///arg.db"


def test_setup_then_status_reports_row_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    tools = _tools()
    db_path = tmp_path / "qai_local.db"
    monkeypatch.setenv("QAI_SQL_URL", f"sqlite:///{db_path}")

    tools.cmd_setup()
    setup_out = capsys.readouterr().out
    assert "sql_health=" in setup_out

    tools.cmd_status()
    status_out = capsys.readouterr().out
    assert "sql_setup_check_rows=" in status_out
    assert "1" in status_out


def test_reset_recreates_db_with_single_bootstrap_row(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    tools = _tools()
    db_path = tmp_path / "qai_local.db"
    monkeypatch.setenv("QAI_SQL_URL", f"sqlite:///{db_path}")

    tools.cmd_setup()
    assert db_path.exists()

    tools.cmd_reset(db_path)
    assert db_path.exists()
    assert tools._status_row_count() == 1


def test_status_json_output_is_parseable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    tools = _tools()
    db_path = tmp_path / "qai_local.db"
    monkeypatch.setenv("QAI_SQL_URL", f"sqlite:///{db_path}")

    tools.cmd_setup()
    _ = capsys.readouterr()

    tools.cmd_status(json_output=True)
    status_json = capsys.readouterr().out.strip()
    payload = json.loads(status_json)

    assert "sql_health" in payload
    assert payload["sql_health"]["enabled"] is True
    assert payload["sql_setup_check_rows"] >= 1


def test_main_status_json_cli(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    tools = _tools()
    db_path = tmp_path / "qai_local.db"
    db_url = f"sqlite:///{db_path}"

    # Seed one row first so CLI status has concrete data.
    monkeypatch.setenv("QAI_SQL_URL", db_url)
    tools.cmd_setup()
    _ = capsys.readouterr()

    monkeypatch.setattr(
        sys,
        "argv",
        ["sql_local_tools.py", "status", "--json", "--url", db_url],
    )
    rc = tools.main()
    output = capsys.readouterr().out.strip()
    payload = json.loads(output)

    assert rc == 0
    assert payload["sql_health"]["enabled"] is True
    assert payload["sql_setup_check_rows"] >= 1


def test_doctor_success_plain_and_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    tools = _tools()
    db_path = tmp_path / "qai_local.db"
    db_url = f"sqlite:///{db_path}"

    monkeypatch.setenv("QAI_SQL_URL", db_url)
    tools.cmd_setup()
    _ = capsys.readouterr()

    rc_plain = tools.cmd_doctor()
    plain_out = capsys.readouterr().out
    assert rc_plain == 0
    assert "healthy" in plain_out.lower()

    rc_json = tools.cmd_doctor(json_output=True)
    json_out = capsys.readouterr().out.strip()
    payload = json.loads(json_out)
    assert rc_json == 0
    assert payload["ok"] is True
    assert payload["sql_health"]["connectivity"] is True


def test_doctor_failure_returns_nonzero_and_json_false(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    tools = _tools()

    def _fake_sql_api():
        return (
            lambda: object(),
            lambda: {
                "enabled": True,
                "connectivity": False,
                "vendor": "sqlite",
                "url": "sqlite:///broken.db",
                "error": "simulated",
            },
        )

    monkeypatch.setattr(tools, "_sql_api", _fake_sql_api)

    rc_plain = tools.cmd_doctor()
    plain_out = capsys.readouterr().out
    assert rc_plain == 1
    assert "unhealthy" in plain_out.lower()

    rc_json = tools.cmd_doctor(json_output=True)
    json_out = capsys.readouterr().out.strip()
    payload = json.loads(json_out)
    assert rc_json == 1
    assert payload["ok"] is False
    assert payload["sql_health"]["connectivity"] is False
