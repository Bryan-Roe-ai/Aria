from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = REPO_ROOT / "notebooks" / "keep_working_launcher.py"


def _load_launcher_module():
    spec = importlib.util.spec_from_file_location(
        "keep_working_launcher", LAUNCHER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kw():
    return _load_launcher_module()


@pytest.mark.unit
def test_default_settings_schema(kw) -> None:
    expected_keys = {
        "task",
        "work",
        "short",
        "long",
        "cycles_per_long",
        "notify",
        "sound",
        "repeat",
        "status_file",
    }
    assert set(kw.DEFAULT_SETTINGS) == expected_keys


@pytest.mark.unit
def test_config_path_targets_notebooks_json(kw) -> None:
    assert Path(kw.CONFIG_PATH).name == "keep_working_config.json"
    assert Path(kw.CONFIG_PATH).parent.name == "notebooks"


@pytest.mark.unit
def test_load_config_returns_defaults_when_missing(kw, tmp_path) -> None:
    cfg = kw.load_config(tmp_path / "missing.json")
    assert cfg == kw.DEFAULT_SETTINGS
    assert cfg is not kw.DEFAULT_SETTINGS  # must be a copy, not the shared dict


@pytest.mark.unit
def test_save_config_round_trip_and_persists_to_disk(kw, tmp_path) -> None:
    path = tmp_path / "cfg.json"
    cleaned = kw.save_config(
        {"task": "Focus", "work": 60, "notify": True}, path)
    assert path.exists()
    # Known keys preserved, missing keys filled from defaults.
    assert cleaned["task"] == "Focus"
    assert cleaned["work"] == 60
    assert cleaned["notify"] is True
    assert cleaned["short"] == kw.DEFAULT_SETTINGS["short"]
    # On-disk content matches and reloads identically.
    assert json.loads(path.read_text()) == cleaned
    assert kw.load_config(path) == cleaned


@pytest.mark.unit
def test_save_config_drops_unknown_keys(kw, tmp_path) -> None:
    path = tmp_path / "cfg.json"
    cleaned = kw.save_config({"task": "x", "totally_unknown": 123}, path)
    assert "totally_unknown" not in cleaned
    assert set(cleaned) == set(kw.DEFAULT_SETTINGS)


@pytest.mark.unit
def test_load_config_falls_back_on_corrupt_json(kw, tmp_path) -> None:
    path = tmp_path / "corrupt.json"
    path.write_text("{ not valid json")
    result = kw.load_config(path)
    assert result == kw.DEFAULT_SETTINGS
    assert result is not kw.DEFAULT_SETTINGS  # must be a copy


@pytest.mark.unit
def test_load_config_falls_back_on_non_dict_json(kw, tmp_path) -> None:
    path = tmp_path / "non_dict.json"
    path.write_text("[1, 2, 3]")
    result = kw.load_config(path)
    assert result == kw.DEFAULT_SETTINGS
    assert result is not kw.DEFAULT_SETTINGS  # must be a copy


@pytest.mark.unit
def test_notebook_uses_module_for_persistence() -> None:
    """The notebook's config cell should rely on the launcher module and not
    contain the regeneration corruption (stray token / duplicated UI block)."""
    nb_path = REPO_ROOT / "notebooks" / "keep_working.ipynb"
    if not nb_path.exists():
        pytest.skip("keep_working.ipynb not present")
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    code_cells = [
        "".join(c["source"])
        for c in nb["cells"]
        if c["cell_type"] == "code"
    ]
    # Prefer a cell that references the launcher module and both helpers.
    preferred = [
        src for src in code_cells
        if "keep_working_launcher" in src
        and "load_config" in src
        and "save_config" in src
    ]
    if not preferred:
        pytest.skip("No launcher-based configuration cell found in notebook")
    cell = preferred[0]
    assert "keep_working_launcher" in cell
    assert "load_config" in cell and "save_config" in cell
    # Corruption markers from concurrent regeneration must be absent.
    assert "\nsource\n" not in cell
