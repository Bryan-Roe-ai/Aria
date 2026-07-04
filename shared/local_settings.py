"""Load Azure Functions-style local.settings.json into process environment."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS_PATH = REPO_ROOT / "local.settings.json"


def _is_comment_key(key: str) -> bool:
    return key.lstrip().startswith("#")


def load_local_settings(path: Path | str | None = None) -> dict[str, str]:
    """Return non-empty Values entries from local.settings.json.

    Comment keys (starting with ``#``) and empty string values are skipped.
    Missing or invalid files return an empty mapping.
    """
    settings_path = Path(path) if path is not None else DEFAULT_SETTINGS_PATH
    if not settings_path.exists():
        return {}

    try:
        payload = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    values = payload.get("Values")
    if not isinstance(values, Mapping):
        return {}

    loaded: dict[str, str] = {}
    for key, value in values.items():
        if not isinstance(key, str) or _is_comment_key(key):
            continue
        if value is None:
            continue
        text = str(value)
        if text == "":
            continue
        loaded[key] = text
    return loaded


def apply_local_settings(
    path: Path | str | None = None,
    *,
    override: bool = False,
) -> dict[str, str]:
    """Apply local.settings.json Values to ``os.environ``.

    By default, existing environment variables are preserved. Set ``override=True``
    to replace values already present in the environment.
    """
    loaded = load_local_settings(path)
    for key, value in loaded.items():
        if override or key not in os.environ:
            os.environ[key] = value
    return loaded
