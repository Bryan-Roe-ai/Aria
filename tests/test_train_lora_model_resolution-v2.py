from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


if importlib.util.find_spec("torch") is None:
    pytest.skip(
        "PyTorch not installed; skipping train_lora model resolution tests",
        allow_module_level=True,
    )


REPO_ROOT = Path(__file__).resolve().parents[1]
TRAIN_LORA_PATH = (
    REPO_ROOT
    / "ai-projects"
    / "lora-training"
    / "microsoft_phi-silica-3.6_v1"
    / "scripts"
    / "train_lora.py"
)

_spec = importlib.util.spec_from_file_location(
    "test_train_lora",
    TRAIN_LORA_PATH,
)
if _spec is None or _spec.loader is None:
    raise ImportError(
        f"Unable to load train_lora module from {TRAIN_LORA_PATH}"
    )
train_lora = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(train_lora)


def test_resolve_hf_model_id_prefers_env_override() -> None:
    resolved = train_lora.resolve_hf_model_id(
        "gpt-oss",
        cli_model_id="microsoft/phi-2",
        env_model_id="openai/gpt-oss-120b",
    )
    assert resolved == "openai/gpt-oss-120b"


def test_resolve_hf_model_id_maps_gpt_oss_alias() -> None:
    resolved = train_lora.resolve_hf_model_id("gpt-oss")
    assert resolved == "openai/gpt-oss-20b"


def test_resolve_hf_model_id_prefers_local_path(tmp_path: Path) -> None:
    checkpoint = tmp_path / "adapter"
    checkpoint.mkdir()

    resolved = train_lora.resolve_hf_model_id(str(checkpoint))
    assert resolved == str(checkpoint)
