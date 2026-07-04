"""Tests for shared.local_settings."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from shared.local_settings import apply_local_settings, load_local_settings


def test_load_local_settings_skips_comment_keys(tmp_path: Path) -> None:
    settings_file = tmp_path / "local.settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "Values": {
                    "# comment key": "",
                    "OLLAMA_MODEL": "llama3.2",
                    "EMPTY": "",
                }
            }
        ),
        encoding="utf-8",
    )

    loaded = load_local_settings(settings_file)

    assert loaded == {"OLLAMA_MODEL": "llama3.2"}


def test_apply_local_settings_does_not_override_existing_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings_file = tmp_path / "local.settings.json"
    settings_file.write_text(
        json.dumps({"Values": {"OLLAMA_MODEL": "from-file", "NEW_KEY": "value"}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("OLLAMA_MODEL", "from-env")

    applied = apply_local_settings(path=settings_file)

    assert applied["OLLAMA_MODEL"] == "from-file"
    assert os.environ["OLLAMA_MODEL"] == "from-env"
    assert os.environ["NEW_KEY"] == "value"
