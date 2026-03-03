#!/usr/bin/env python3
"""
Custom LLM From Scratch (PyTorch)
=================================

A lightweight decoder-only transformer that can be trained on Aria chat
datasets without depending on HuggingFace model architectures.

Features:
- Word-level tokenizer built from local dataset
- Decoder-only transformer with causal self-attention
- Train CLI + generate CLI
- Supports JSON / JSONL / directory-based chat datasets
- Saves checkpoints + tokenizer + metrics for reuse

Examples:
    python scripts/custom_llm_from_scratch.py train \
        --dataset datasets/chat/aria_persona \
        --output-dir data_out/custom_llm \
        --epochs 2 --batch-size 8

    python scripts/custom_llm_from_scratch.py generate \
        --checkpoint data_out/custom_llm/model.pt \
        --tokenizer data_out/custom_llm/tokenizer.json \
        --prompt "Who are you?"
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset


LOGGER = logging.getLogger("custom_llm")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


SPECIAL_TOKENS = ["<pad>", "<bos>", "<eos>", "<unk>"]


@dataclass
class ModelConfig:
    vocab_size: int
    d_model: int = 256
    n_heads: int = 4
    n_layers: int = 4
    d_ff: int = 1024
    max_seq_len: int = 128
    dropout: float = 0.1


@dataclass
class TrainConfig:
    epochs: int = 3
    batch_size: int = 16
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    val_split: float = 0.1
    seed: int = 42


class SimpleWordTokenizer:
    """Minimal word-level tokenizer suitable for a compact custom model."""

    def __init__(self, token_to_id: Dict[str, int]) -> None:
        self.token_to_id = token_to_id
        self.id_to_token = {v: k for k, v in token_to_id.items()}

        self.pad_id = token_to_id["<pad>"]
        self.bos_id = token_to_id["<bos>"]
        self.eos_id = token_to_id["<eos>"]
        self.unk_id = token_to_id["<unk>"]

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\w+|[^\w\s]", text.lower(), re.UNICODE)

    @classmethod
    def build(
        cls,
        texts: Sequence[str],
        vocab_size: int = 8000,
        min_freq: int = 2,
    ) -> "SimpleWordTokenizer":
        freq: Dict[str, int] = {}
        for text in texts:
            for tok in cls._tokenize(text):
                freq[tok] = freq.get(tok, 0) + 1

        sorted_tokens = sorted(
            [t for t, c in freq.items() if c >= min_freq],
            key=lambda t: (-freq[t], t),
        )
        sorted_tokens = sorted_tokens[: max(0, vocab_size - len(SPECIAL_TOKENS))]

        token_to_id = {tok: idx for idx, tok in enumerate(SPECIAL_TOKENS)}
        for tok in sorted_tokens:
            token_to_id[tok] = len(token_to_id)

        return cls(token_to_id)

    def encode(self, text: str, add_special: bool = True) -> List[int]:
        ids = [self.token_to_id.get(tok, self.unk_id) for tok in self._tokenize(text)]
        if add_special:
            return [self.bos_id] + ids + [self.eos_id]
        return ids

    def decode(self, ids: Iterable[int], skip_special: bool = True) -> str:
        out_tokens: List[str] = []
        specials = set(SPECIAL_TOKENS)
        for idx in ids:
            tok = self.id_to_token.get(int(idx), "<unk>")
            if skip_special and tok in specials:
                continue
            out_tokens.append(tok)

        text = " ".join(out_tokens)
        # basic detokenization for punctuation
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        return text.strip()

    def save(self, path: Path) -> None:
        payload = {"token_to_id": self.token_to_id}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "SimpleWordTokenizer":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(payload["token_to_id"])


def _extract_text_from_item(item: Any) -> str:
    if isinstance(item, str):
        return item

    if not isinstance(item, dict):
        return str(item)

    if "messages" in item and isinstance(item["messages"], list):
        parts: List[str] = []
        for msg in item["messages"]:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role", "user")
            content = str(msg.get("content", "")).strip()
            if content:
                parts.append(f"{role}: {content}")
        return "\n".join(parts)

    if "instruction" in item and "output" in item:
        instruction = str(item.get("instruction", "")).strip()
        input_text = str(item.get("input", "")).strip()
        output = str(item.get("output", "")).strip()
        if input_text:
            return f"instruction: {instruction}\ninput: {input_text}\nassistant: {output}"
        return f"instruction: {instruction}\nassistant: {output}"

    if "text" in item:
        return str(item["text"])

    return json.dumps(item, ensure_ascii=False)


def load_chat_texts(dataset_path: Path) -> List[str]:
    """Load training texts from .json, .jsonl, or dataset directories."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

    files: List[Path] = []
    if dataset_path.is_file():
        files = [dataset_path]
    else:
        files.extend(dataset_path.rglob("train.json"))
        files.extend(dataset_path.rglob("train.jsonl"))
        if not files:
            files.extend(dataset_path.rglob("*.json"))
            files.extend(dataset_path.rglob("*.jsonl"))

    texts: List[str] = []
    for file_path in sorted(set(files)):
        if file_path.suffix == ".jsonl":
            for line in file_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    texts.append(_extract_text_from_item(json.loads(line)))
                except json.JSONDecodeError:
                    continue
        elif file_path.suffix == ".json":
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue

            if isinstance(data, list):
                texts.extend(_extract_text_from_item(item) for item in data)
            else:
                texts.append(_extract_text_from_item(data))

    cleaned = [t.strip() for t in texts if t and t.strip()]
    if not cleaned:
        raise ValueError(f"No usable text samples found in {dataset_path}")
    return cleaned


class LMDataset(Dataset[torch.Tensor]):
    """Creates fixed-length token windows for autoregressive training."""

    def __init__(
        self,
        texts: Sequence[str],
        tokenizer: SimpleWordTokenizer,
        seq_len: int,
    ) -> None:
        self.samples: List[torch.Tensor] = []

        for text in texts:
            token_ids = tokenizer.encode(text, add_special=True)
            if len(token_ids) < 2:
                continue

            step = max(8, seq_len // 2)
            for start in range(0, len(token_ids) - 1, step):
                chunk = token_ids[start : start + seq_len + 1]
                if len(chunk) < 2:
                    continue
                if len(chunk) < seq_len + 1:
                    chunk = chunk + [tokenizer.pad_id] * (seq_len + 1 - len(chunk))
                self.samples.append(torch.tensor(chunk, dtype=torch.long))

        if not self.samples:
            raise ValueError("Dataset produced 0 token chunks. Increase data or lower seq_len.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return self.samples[idx]


class CausalSelfAttention(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        if config.d_model % config.n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")

        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads

        self.qkv = nn.Linear(config.d_model, 3 * config.d_model)
        self.out_proj = nn.Linear(config.d_model, config.d_model)
        self.dropout = nn.Dropout(config.dropout)

        mask = torch.tril(torch.ones(config.max_seq_len, config.max_seq_len))
        self.register_buffer("causal_mask", mask.view(1, 1, config.max_seq_len, config.max_seq_len))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        bsz, seq_len, d_model = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.chunk(3, dim=-1)

        q = q.view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(bsz, seq_len, self.n_heads, self.head_dim).transpose(1, 2)

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        mask = self.causal_mask[:, :, :seq_len, :seq_len]
        scores = scores.masked_fill(mask == 0, float("-inf"))

        attn = torch.softmax(scores, dim=-1)
        attn = self.dropout(attn)

        out = attn @ v
        out = out.transpose(1, 2).contiguous().view(bsz, seq_len, d_model)
        return self.out_proj(out)


class TransformerBlock(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(config.d_model)
        self.attn = CausalSelfAttention(config)
        self.ln2 = nn.LayerNorm(config.d_model)
        self.ffn = nn.Sequential(
            nn.Linear(config.d_model, config.d_ff),
            nn.GELU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.d_ff, config.d_model),
            nn.Dropout(config.dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class CustomTransformerLM(nn.Module):
    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.config = config

        self.token_emb = nn.Embedding(config.vocab_size, config.d_model)
        self.pos_emb = nn.Embedding(config.max_seq_len, config.d_model)
        self.dropout = nn.Dropout(config.dropout)
        self.blocks = nn.ModuleList([TransformerBlock(config) for _ in range(config.n_layers)])
        self.ln_f = nn.LayerNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

        # Tie token embedding and output projection
        self.lm_head.weight = self.token_emb.weight

    def forward(self, input_ids: torch.Tensor, targets: torch.Tensor | None = None) -> Dict[str, torch.Tensor]:
        bsz, seq_len = input_ids.shape
        if seq_len > self.config.max_seq_len:
            raise ValueError(
                f"Input length {seq_len} exceeds model max_seq_len {self.config.max_seq_len}"
            )

        pos = torch.arange(0, seq_len, device=input_ids.device).unsqueeze(0)
        x = self.token_emb(input_ids) + self.pos_emb(pos)
        x = self.dropout(x)

        for block in self.blocks:
            x = block(x)

        x = self.ln_f(x)
        logits = self.lm_head(x)

        out: Dict[str, torch.Tensor] = {"logits": logits}
        if targets is not None:
            loss = F.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                targets.reshape(-1),
                ignore_index=0,  # pad token id
            )
            out["loss"] = loss
        return out

    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int = 64,
        temperature: float = 1.0,
        top_k: int = 40,
        eos_id: int | None = None,
    ) -> torch.Tensor:
        self.eval()
        ids = input_ids

        for _ in range(max_new_tokens):
            ctx = ids[:, -self.config.max_seq_len :]
            logits = self(ctx)["logits"][:, -1, :]
            logits = logits / max(temperature, 1e-6)

            if top_k > 0:
                values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits = torch.where(logits < values[:, [-1]], torch.full_like(logits, -float("inf")), logits)

            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            ids = torch.cat([ids, next_token], dim=1)

            if eos_id is not None and torch.all(next_token == eos_id):
                break

        return ids


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def split_train_val(items: Sequence[str], val_split: float, seed: int) -> tuple[List[str], List[str]]:
    items = list(items)
    rng = random.Random(seed)
    rng.shuffle(items)
    n_val = max(1, int(len(items) * val_split)) if len(items) > 1 else 0
    if n_val == 0:
        return items, []
    return items[n_val:], items[:n_val]


def evaluate_loss(model: CustomTransformerLM, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    losses: List[float] = []
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            x = batch[:, :-1]
            y = batch[:, 1:]
            out = model(x, y)
            losses.append(float(out["loss"].item()))
    if not losses:
        return 0.0
    return sum(losses) / len(losses)


def run_training(args: argparse.Namespace) -> Path:
    set_seed(args.seed)

    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    texts = load_chat_texts(dataset_path)
    LOGGER.info("Loaded %d text samples", len(texts))

    train_texts, val_texts = split_train_val(texts, args.val_split, args.seed)

    tokenizer = SimpleWordTokenizer.build(
        train_texts,
        vocab_size=args.vocab_size,
        min_freq=args.min_freq,
    )
    tokenizer_path = output_dir / "tokenizer.json"
    tokenizer.save(tokenizer_path)

    train_ds = LMDataset(train_texts, tokenizer, seq_len=args.max_seq_len)
    val_ds = LMDataset(val_texts, tokenizer, seq_len=args.max_seq_len) if val_texts else None

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size) if val_ds is not None else None

    model_config = ModelConfig(
        vocab_size=len(tokenizer.token_to_id),
        d_model=args.d_model,
        n_heads=args.n_heads,
        n_layers=args.n_layers,
        d_ff=args.d_ff,
        max_seq_len=args.max_seq_len,
        dropout=args.dropout,
    )

    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    model = CustomTransformerLM(model_config).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    metrics: Dict[str, Any] = {
        "train_loss": [],
        "val_loss": [],
        "config": {
            "model": asdict(model_config),
            "train": {
                "epochs": args.epochs,
                "batch_size": args.batch_size,
                "learning_rate": args.learning_rate,
                "weight_decay": args.weight_decay,
                "seed": args.seed,
            },
        },
    }

    for epoch in range(args.epochs):
        model.train()
        losses: List[float] = []

        for batch in train_loader:
            batch = batch.to(device)
            x = batch[:, :-1]
            y = batch[:, 1:]

            out = model(x, y)
            loss = out["loss"]
            loss.backward()

            if args.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)

            optimizer.step()
            optimizer.zero_grad(set_to_none=True)
            losses.append(float(loss.item()))

        epoch_train_loss = sum(losses) / max(1, len(losses))
        metrics["train_loss"].append(epoch_train_loss)

        epoch_val_loss = evaluate_loss(model, val_loader, device) if val_loader is not None else 0.0
        metrics["val_loss"].append(epoch_val_loss)

        LOGGER.info(
            "Epoch %d/%d - train_loss=%.4f val_loss=%.4f",
            epoch + 1,
            args.epochs,
            epoch_train_loss,
            epoch_val_loss,
        )

    checkpoint = {
        "model_state": model.state_dict(),
        "model_config": asdict(model_config),
        "optimizer_state": optimizer.state_dict(),
    }
    checkpoint_path = output_dir / "model.pt"
    torch.save(checkpoint, checkpoint_path)

    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    LOGGER.info("Saved checkpoint to %s", checkpoint_path)
    LOGGER.info("Saved tokenizer to %s", tokenizer_path)
    return checkpoint_path


def run_training_from_config(
    dataset: str | Path,
    output_dir: str | Path,
    overrides: Dict[str, Any] | None = None,
) -> Path:
    """Programmatic entrypoint for embedding custom-architecture training in other scripts."""
    args = argparse.Namespace(
        command="train",
        dataset=str(dataset),
        output_dir=str(output_dir),
        epochs=3,
        batch_size=16,
        learning_rate=3e-4,
        weight_decay=0.01,
        grad_clip=1.0,
        val_split=0.1,
        seed=42,
        vocab_size=8000,
        min_freq=2,
        max_seq_len=128,
        d_model=256,
        n_heads=4,
        n_layers=4,
        d_ff=1024,
        dropout=0.1,
        cpu=False,
    )
    if overrides:
        for key, value in overrides.items():
            if hasattr(args, key):
                setattr(args, key, value)

    return run_training(args)


def run_generation(args: argparse.Namespace) -> str:
    checkpoint_path = Path(args.checkpoint)
    tokenizer_path = Path(args.tokenizer)

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    if not tokenizer_path.exists():
        raise FileNotFoundError(f"Tokenizer not found: {tokenizer_path}")

    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model_config = ModelConfig(**checkpoint["model_config"])
    model = CustomTransformerLM(model_config)
    model.load_state_dict(checkpoint["model_state"])

    tokenizer = SimpleWordTokenizer.load(tokenizer_path)

    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    model.to(device)

    input_ids = tokenizer.encode(args.prompt, add_special=True)
    input_tensor = torch.tensor([input_ids], dtype=torch.long, device=device)

    output = model.generate(
        input_tensor,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        eos_id=tokenizer.eos_id,
    )

    return tokenizer.decode(output[0].tolist(), skip_special=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a custom decoder-only LLM from scratch")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train model from dataset")
    train_parser.add_argument("--dataset", type=str, required=True, help="Path to chat dataset (file or dir)")
    train_parser.add_argument("--output-dir", type=str, default="data_out/custom_llm", help="Where model artifacts are saved")
    train_parser.add_argument("--epochs", type=int, default=3)
    train_parser.add_argument("--batch-size", type=int, default=16)
    train_parser.add_argument("--learning-rate", type=float, default=3e-4)
    train_parser.add_argument("--weight-decay", type=float, default=0.01)
    train_parser.add_argument("--grad-clip", type=float, default=1.0)
    train_parser.add_argument("--val-split", type=float, default=0.1)
    train_parser.add_argument("--seed", type=int, default=42)

    train_parser.add_argument("--vocab-size", type=int, default=8000)
    train_parser.add_argument("--min-freq", type=int, default=2)

    train_parser.add_argument("--max-seq-len", type=int, default=128)
    train_parser.add_argument("--d-model", type=int, default=256)
    train_parser.add_argument("--n-heads", type=int, default=4)
    train_parser.add_argument("--n-layers", type=int, default=4)
    train_parser.add_argument("--d-ff", type=int, default=1024)
    train_parser.add_argument("--dropout", type=float, default=0.1)
    train_parser.add_argument("--cpu", action="store_true", help="Force CPU even if CUDA is available")

    gen_parser = subparsers.add_parser("generate", help="Generate text from checkpoint")
    gen_parser.add_argument("--checkpoint", type=str, required=True)
    gen_parser.add_argument("--tokenizer", type=str, required=True)
    gen_parser.add_argument("--prompt", type=str, required=True)
    gen_parser.add_argument("--max-new-tokens", type=int, default=64)
    gen_parser.add_argument("--temperature", type=float, default=0.8)
    gen_parser.add_argument("--top-k", type=int, default=40)
    gen_parser.add_argument("--cpu", action="store_true", help="Force CPU even if CUDA is available")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "train":
        run_training(args)
        return 0

    if args.command == "generate":
        text = run_generation(args)
        print(text)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
