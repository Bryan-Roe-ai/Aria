#!/usr/bin/env python3
"""Verify DAB connection-string setup across local config surfaces.

Checks:
- `Database_20260705.json` and `Database_20260620.json` parse as JSON.
- Each DAB config has either:
    - `data-source.connection-string` as `${DAB_CONNECTION_STRING}` or
    - a direct non-empty connection string.
- `local.settings.json` and `local.settings.json.example` include
  `Values.DAB_CONNECTION_STRING` as a non-empty string.
- `.env.example` includes a `DAB_CONNECTION_STRING=` entry.

By default, placeholder values emit warnings. Set `DAB_VERIFY_STRICT_VALUES=1`
to escalate placeholder warnings into failures.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

REQUIRED_JSON_FILES = [
    "Database_20260705.json",
    "Database_20260620.json",
]

PLACEHOLDER_SNIPPETS = (
    "undefined",
    "changeme",
    "replace_me",
    "<server>",
    "<database>",
    "database=database",
    "initial catalog=database",
    "server=tcp:example",
)


def _placeholder_hits(value: str) -> list[str]:
    lower = value.lower()
    return [snippet for snippet in PLACEHOLDER_SNIPPETS if snippet in lower]


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"error=missing_file:{path.name}"
    except json.JSONDecodeError as exc:
        return None, f"error=invalid_json:{path.name}:{exc.msg}"

    if not isinstance(data, dict):
        return None, f"error=invalid_json_root:{path.name}:expected_object"
    return data, None


def check_database_config(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    data, err = _load_json(path)
    if err:
        errors.append(err)
        return errors, warnings

    ds = data.get("data-source")
    if not isinstance(ds, dict):
        errors.append(f"error=missing_data_source:{path.name}")
        return errors, warnings

    conn = ds.get("connection-string")
    if not isinstance(conn, str) or not conn.strip():
        errors.append(f"error=missing_connection_string:{path.name}")
        return errors, warnings

    conn = conn.strip()
    if conn.startswith("${") and conn.endswith("}"):
        var_name = conn[2:-1]
        if var_name != "DAB_CONNECTION_STRING":
            errors.append(
                f"error=unexpected_connection_env_ref:{path.name}:{var_name}:expected:DAB_CONNECTION_STRING",
            )
    else:
        hits = _placeholder_hits(conn)
        if hits:
            warnings.append(
                f"warning=placeholder_connection_string:{path.name}:{','.join(hits)}",
            )
    return errors, warnings


def check_local_settings(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    data, err = _load_json(path)
    if err:
        errors.append(err)
        return errors, warnings

    values = data.get("Values")
    if not isinstance(values, dict):
        return [f"error=missing_values:{path.name}"], warnings

    conn = values.get("DAB_CONNECTION_STRING")
    if not isinstance(conn, str) or not conn.strip():
        errors.append(f"error=missing_key:{path.name}:DAB_CONNECTION_STRING")
    else:
        hits = _placeholder_hits(conn)
        if hits:
            warnings.append(
                f"warning=placeholder_connection_string:{path.name}:{','.join(hits)}",
            )

    return errors, warnings


def check_env_example(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"error=missing_file:{path.name}"], warnings

    found = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("DAB_CONNECTION_STRING="):
            found = True
            _, value = line.split("=", 1)
            hits = _placeholder_hits(value)
            if hits:
                warnings.append(
                    f"warning=placeholder_connection_string:{path.name}:{','.join(hits)}",
                )
            break

    if not found:
        errors.append("error=missing_key:.env.example:DAB_CONNECTION_STRING")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify DAB setup wiring")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Repository root")
    args = parser.parse_args()

    root = args.repo_root.resolve()

    errors: list[str] = []
    warnings: list[str] = []

    for file_name in REQUIRED_JSON_FILES:
        cfg_errors, cfg_warnings = check_database_config(root / file_name)
        errors.extend(cfg_errors)
        warnings.extend(cfg_warnings)

    for file_name in ("local.settings.json", "local.settings.json.example"):
        local_errors, local_warnings = check_local_settings(root / file_name)
        errors.extend(local_errors)
        warnings.extend(local_warnings)

    env_errors, env_warnings = check_env_example(root / ".env.example")
    errors.extend(env_errors)
    warnings.extend(env_warnings)

    strict_values = os.getenv("DAB_VERIFY_STRICT_VALUES", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if strict_values:
        errors.extend([warning.replace("warning=", "error=") for warning in warnings])

    for warning in warnings:
        print(warning)

    if errors:
        for err in errors:
            print(err)
        return 1

    print("ok=dab_verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
