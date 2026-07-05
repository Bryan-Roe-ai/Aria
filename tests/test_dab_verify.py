from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from scripts.dab_verify import check_database_config, check_env_example, check_local_settings, main


def _write(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_check_database_config_accepts_env_ref(tmp_path: Path) -> None:
    p = tmp_path / "Database_20260705.json"
    _write(
        p,
        {
            "$schema": "https://github.com/Azure/data-api-builder/releases/latest/download/dab.draft.schema.json",
            "data-source": {
                "database-type": "mssql",
                "connection-string": "${DAB_CONNECTION_STRING}",
            },
            "runtime": {"rest": {"enabled": True}, "host": {"mode": "development"}},
            "entities": {},
        },
    )

    errors, warnings = check_database_config(p)
    assert errors == []
    assert warnings == []


def test_check_database_config_rejects_wrong_env_ref(tmp_path: Path) -> None:
    p = tmp_path / "Database_20260705.json"
    _write(
        p,
        {
            "data-source": {
                "database-type": "mssql",
                "connection-string": "${NOT_DAB_CONNECTION_STRING}",
            }
        },
    )

    errors, warnings = check_database_config(p)
    assert warnings == []
    assert any("unexpected_connection_env_ref" in e for e in errors)


def test_check_database_config_warns_placeholder_direct_conn(tmp_path: Path) -> None:
    p = tmp_path / "Database_20260705.json"
    _write(
        p,
        {
            "data-source": {
                "database-type": "mssql",
                "connection-string": "Server=tcp:aria-24563.database.windows.net;Database=undefined;",
            }
        },
    )

    errors, warnings = check_database_config(p)
    assert errors == []
    assert any("placeholder_connection_string" in w for w in warnings)


def test_check_local_settings_requires_key(tmp_path: Path) -> None:
    p = tmp_path / "local.settings.json"
    _write(p, {"IsEncrypted": False, "Values": {}})

    errors, warnings = check_local_settings(p)
    assert warnings == []
    assert any("missing_key" in e for e in errors)


def test_check_local_settings_warns_placeholder_value(tmp_path: Path) -> None:
    p = tmp_path / "local.settings.json"
    _write(
        p,
        {
            "IsEncrypted": False,
            "Values": {
                "DAB_CONNECTION_STRING": "Server=tcp:aria-24563.database.windows.net;Database=undefined;",
            },
        },
    )

    errors, warnings = check_local_settings(p)
    assert errors == []
    assert any("placeholder_connection_string" in w for w in warnings)


def test_check_env_example_requires_key(tmp_path: Path) -> None:
    p = tmp_path / ".env.example"
    p.write_text("# no DAB key here\n", encoding="utf-8")

    errors, warnings = check_env_example(p)
    assert warnings == []
    assert any("missing_key:.env.example:DAB_CONNECTION_STRING" in e for e in errors)


def test_check_env_example_warns_placeholder_value(tmp_path: Path) -> None:
    p = tmp_path / ".env.example"
    p.write_text(
        "DAB_CONNECTION_STRING=Server=tcp:aria-24563.database.windows.net;Database=undefined;\n",
        encoding="utf-8",
    )

    errors, warnings = check_env_example(p)
    assert errors == []
    assert any("placeholder_connection_string" in w for w in warnings)


def _write_minimal_repo(root: Path) -> None:
    for name in ("Database_20260705.json", "Database_20260620.json"):
        _write(
            root / name,
            {
                "$schema": "https://github.com/Azure/data-api-builder/releases/latest/download/dab.draft.schema.json",
                "data-source": {
                    "database-type": "mssql",
                    "connection-string": "${DAB_CONNECTION_STRING}",
                },
                "runtime": {"rest": {"enabled": True}, "host": {"mode": "development"}},
                "entities": {},
            },
        )

    _write(
        root / "local.settings.json",
        {"IsEncrypted": False, "Values": {"DAB_CONNECTION_STRING": "Server=tcp:good;Database=Aria;"}},
    )
    _write(
        root / "local.settings.json.example",
        {"IsEncrypted": False, "Values": {"DAB_CONNECTION_STRING": "Server=tcp:good;Database=Aria;"}},
    )
    (root / ".env.example").write_text(
        "DAB_CONNECTION_STRING=Server=tcp:good;Database=Aria;\n",
        encoding="utf-8",
    )


def test_main_ok_minimal_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_minimal_repo(tmp_path)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(os, "environ", os.environ.copy())
    monkeypatch.setattr("sys.argv", ["dab_verify.py", "--repo-root", str(tmp_path)])

    assert main() == 0


def test_main_fails_when_strict_and_placeholders(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_minimal_repo(tmp_path)

    # Introduce placeholder token that should fail in strict mode only.
    _write(
        tmp_path / "local.settings.json",
        {
            "IsEncrypted": False,
            "Values": {
                "DAB_CONNECTION_STRING": "Server=tcp:aria-24563.database.windows.net;Database=undefined;",
            },
        },
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DAB_VERIFY_STRICT_VALUES", "1")
    monkeypatch.setattr("sys.argv", ["dab_verify.py", "--repo-root", str(tmp_path)])

    assert main() == 1
