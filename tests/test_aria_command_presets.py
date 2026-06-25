"""Structural checks for Quantum Lab command preset pack (no server required)."""

import json
from pathlib import Path

PRESETS_PATH = Path(__file__).parent.parent / "apps" / "aria" / "command_presets.generated.json"

QUANTUM_LAB_COMMANDS = [
    "wave and say welcome to the quantum lab",
    "look at the qubit",
    "pick up qubit",
    "move to the gate and nod",
    "bow and say measurement complete",
]


def _load_presets() -> dict:
    return json.loads(PRESETS_PATH.read_text(encoding="utf-8"))


def test_command_presets_file_is_valid_json() -> None:
    payload = _load_presets()
    assert isinstance(payload.get("presets"), list), "Root presets key must be a list"
    assert payload["presets"], "Preset list must not be empty"


def test_quantum_lab_group_has_five_curated_commands() -> None:
    payload = _load_presets()
    quantum_groups = [g for g in payload["presets"] if g.get("name") == "Quantum Lab"]
    assert len(quantum_groups) == 1, "Exactly one Quantum Lab preset group expected"

    commands = quantum_groups[0]["commands"]
    assert len(commands) >= 5, "Quantum Lab pack should expose at least five commands"
    for expected in QUANTUM_LAB_COMMANDS:
        assert expected in commands, f"Missing planned command: {expected}"


def test_quantum_lab_commands_reference_stage_objects() -> None:
    payload = _load_presets()
    quantum = next(g for g in payload["presets"] if g.get("name") == "Quantum Lab")
    joined = " ".join(quantum["commands"]).lower()
    assert "qubit" in joined, "Quantum Lab commands should reference qubit object"
    assert "gate" in joined, "Quantum Lab commands should reference gate object"
