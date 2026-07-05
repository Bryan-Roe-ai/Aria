from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

pytestmark = pytest.mark.unit


def _dab_verify() -> Any:
    import scripts.dab_verify as dab_verify

    return dab_verify


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_required_files(tmp_path: Path) -> None:
    conn_ref = "@env('DAB_CONNECTION_STRING')"
    _write_json(
        tmp_path / "Database_20260705.json",
        {"data-source": {"connection-string": conn_ref}},
    )
    _write_json(
        tmp_path / "Database_20260620.json",
        {"data-source": {"connection-string": conn_ref}},
    )
    _write_json(
        tmp_path / "local.settings.json",
        {"Values": {"DAB_CONNECTION_STRING": "Server=tcp:example"}},
    )
    _write_json(
        tmp_path / "local.settings.json.example",
        {"Values": {"DAB_CONNECTION_STRING": "Server=tcp:example"}},
    )


def test_dab_verify_main_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    dab_verify = _dab_verify()
    _seed_required_files(tmp_path)
    (tmp_path / ".env.example").write_text(
        "DAB_CONNECTION_STRING=Server=tcp:example;",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    assert dab_verify.main() == 0


def test_dab_verify_main_fails_when_env_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    dab_verify = _dab_verify()
    _seed_required_files(tmp_path)
    (tmp_path / ".env.example").write_text("", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    assert dab_verify.main() == 1
