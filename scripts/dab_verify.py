"""Verify Data API Builder (DAB) config and env wiring consistency."""

from __future__ import annotations

import json
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    required_json_files = [
        Path("Database_20260705.json"),
        Path("Database_20260620.json"),
        Path("local.settings.json"),
        Path("local.settings.json.example"),
    ]

    for file_path in required_json_files:
        _load_json(file_path)

    cfg_current = _load_json(Path("Database_20260705.json"))
    cfg_legacy = _load_json(Path("Database_20260620.json"))
    local_values = _load_json(Path("local.settings.json")).get("Values", {})
    example_values = _load_json(Path("local.settings.json.example")).get("Values", {})
    env_path = Path(".env.example")
    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8")
    else:
        env_text = ""

    checks = {
        "db_current_uses_env": (cfg_current["data-source"]["connection-string"] == "@env('DAB_CONNECTION_STRING')"),
        "db_legacy_uses_env": (cfg_legacy["data-source"]["connection-string"] == "@env('DAB_CONNECTION_STRING')"),
        "local_has_dab_connection": "DAB_CONNECTION_STRING" in local_values,
        "example_has_dab_connection": ("DAB_CONNECTION_STRING" in example_values),
        "env_example_has_dab_connection": "DAB_CONNECTION_STRING=" in env_text,
    }

    for name, ok in checks.items():
        print(f"{name}={ok}")

    if not all(checks.values()):
        return 1

    print("✅ DAB verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
