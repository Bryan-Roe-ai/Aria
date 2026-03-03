"""Unit tests for custom LLM from-scratch implementation."""

from __future__ import annotations

import json
import importlib
import sys
from pathlib import Path

import pytest
import torch

# Add scripts directory to path (consistent with existing tests)
SCRIPTS_PATH = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_PATH))

custom_llm = importlib.import_module("custom_llm_from_scratch")

CustomTransformerLM = custom_llm.CustomTransformerLM
ModelConfig = custom_llm.ModelConfig
SimpleWordTokenizer = custom_llm.SimpleWordTokenizer
build_parser = custom_llm.build_parser
load_chat_texts = custom_llm.load_chat_texts
run_generation = custom_llm.run_generation
run_training = custom_llm.run_training


@pytest.mark.unit
def test_tokenizer_roundtrip():
    texts = ["hello world", "aria assistant is helpful"]
    tok = SimpleWordTokenizer.build(texts, vocab_size=64, min_freq=1)
    ids = tok.encode("hello aria", add_special=True)

    assert ids[0] == tok.bos_id
    assert ids[-1] == tok.eos_id

    decoded = tok.decode(ids)
    assert "hello" in decoded


@pytest.mark.unit
def test_model_forward_shape():
    cfg = ModelConfig(vocab_size=128, d_model=64, n_heads=4, n_layers=2, d_ff=128, max_seq_len=16)
    model = CustomTransformerLM(cfg)

    x = torch.randint(0, cfg.vocab_size, (2, 16))
    y = torch.randint(0, cfg.vocab_size, (2, 16))

    out = model(x, y)
    assert "logits" in out
    assert "loss" in out
    assert out["logits"].shape == (2, 16, cfg.vocab_size)
    assert out["loss"].item() >= 0


@pytest.mark.unit
def test_dataset_loader_supports_instruction_json(tmp_path: Path):
    d = tmp_path / "dataset"
    d.mkdir(parents=True)

    data = [
        {"instruction": "Say hi", "input": "", "output": "Hi there"},
        {"instruction": "Who are you?", "input": "", "output": "I am Aria"},
    ]

    (d / "train.json").write_text(json.dumps(data), encoding="utf-8")
    texts = load_chat_texts(d)

    assert len(texts) == 2
    assert "assistant:" in texts[0]


@pytest.mark.unit
def test_smoke_train_and_generate(tmp_path: Path):
    dataset_dir = tmp_path / "chat"
    dataset_dir.mkdir(parents=True)

    samples = [
        {"messages": [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]},
        {"messages": [{"role": "user", "content": "who are you"}, {"role": "assistant", "content": "i am aria"}]},
        {"messages": [{"role": "user", "content": "what can you do"}, {"role": "assistant", "content": "i can help"}]},
    ]
    (dataset_dir / "train.json").write_text(json.dumps(samples), encoding="utf-8")

    output_dir = tmp_path / "out"

    train_parser = build_parser()
    train_args = train_parser.parse_args(
        [
            "train",
            "--dataset",
            str(dataset_dir),
            "--output-dir",
            str(output_dir),
            "--epochs",
            "1",
            "--batch-size",
            "2",
            "--max-seq-len",
            "16",
            "--d-model",
            "32",
            "--n-heads",
            "4",
            "--n-layers",
            "2",
            "--d-ff",
            "64",
            "--vocab-size",
            "128",
            "--min-freq",
            "1",
            "--cpu",
        ]
    )

    ckpt = run_training(train_args)
    assert ckpt.exists()
    assert (output_dir / "tokenizer.json").exists()

    gen_parser = build_parser()
    gen_args = gen_parser.parse_args(
        [
            "generate",
            "--checkpoint",
            str(output_dir / "model.pt"),
            "--tokenizer",
            str(output_dir / "tokenizer.json"),
            "--prompt",
            "user: hello",
            "--max-new-tokens",
            "8",
            "--cpu",
        ]
    )

    text = run_generation(gen_args)
    assert isinstance(text, str)
    assert len(text) > 0
