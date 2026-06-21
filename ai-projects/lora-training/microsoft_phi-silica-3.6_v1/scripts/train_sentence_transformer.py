#!/usr/bin/env python3
"""Fine-tune a SentenceTransformer bi-encoder (production template from HF skill).

Default base model matches Aria RAG (`all-MiniLM-L6-v2`). Default dataset is
`sentence-transformers/all-nli` (triplet) with MultipleNegativesRankingLoss.

Examples:

    pip install "sentence-transformers[train]>=5.0" datasets accelerate trackio

    # Smoke test (max_steps=1, tiny slice, no Hub push)
    SMOKE_TEST=1 python scripts/train_sentence_transformer.py

    # Full local run
    python scripts/train_sentence_transformer.py \\
        --dataset sentence-transformers/all-nli \\
        --subset triplet \\
        --model sentence-transformers/all-MiniLM-L6-v2 \\
        --run-name minilm-all-nli

    # Custom Hub dataset (must match MNRL: anchor/positive or anchor/positive/negative columns)
    python scripts/train_sentence_transformer.py \\
        --dataset your-org/your-dataset \\
        --train-split train \\
        --eval-split validation
"""

from __future__ import annotations

import argparse
import logging
import os
from contextlib import nullcontext
from pathlib import Path

import torch
from datasets import load_dataset

from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerModelCardData,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
)
from sentence_transformers.base.sampler import BatchSamplers
from sentence_transformers.sentence_transformer.evaluation import NanoBEIREvaluator
from sentence_transformers.sentence_transformer.losses import MultipleNegativesRankingLoss

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "data_out" / "sentence_transformer_training"


def autocast_ctx():
    if not torch.cuda.is_available():
        return nullcontext()
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return torch.autocast("cuda", dtype=dtype)


def log_trackio_dashboard():
    try:
        from huggingface_hub import whoami

        hf_user = whoami().get("name")
        if hf_user:
            logging.info(
                "Trackio dashboard: https://huggingface.co/spaces/%s/trackio",
                hf_user,
            )
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a SentenceTransformer bi-encoder")
    parser.add_argument(
        "--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--dataset", default="sentence-transformers/all-nli")
    parser.add_argument("--subset", default="triplet",
                        help="Dataset config name (if any)")
    parser.add_argument("--train-split", default="train")
    parser.add_argument("--eval-split", default="dev")
    parser.add_argument("--train-size", type=int, default=50_000)
    parser.add_argument("--eval-size", type=int, default=1_000)
    parser.add_argument("--run-name", default="minilm-all-nli")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Defaults to data_out/sentence_transformer_training/<run-name>",
    )
    parser.add_argument(
        "--eval-only",
        default=None,
        help="Skip training; load saved model path and run evaluator only",
    )
    parser.add_argument("--hub-model-id", default=None)
    parser.add_argument("--push-to-hub", action="store_true")
    return parser.parse_args()


def setup_logging(run_name: str, output_dir: str | None = None) -> None:
    log_dir = (
        Path(output_dir) / "logs"
        if output_dir
        else REPO_ROOT / "data_out" / "sentence_transformer_training" / "logs"
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / f"{run_name}.log"),
        ],
        force=True,
    )
    for noisy in ("httpx", "httpcore", "huggingface_hub", "urllib3", "filelock", "fsspec"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    if torch.cuda.is_available():
        torch.set_float32_matmul_precision("high")


def load_split(name: str, subset: str | None, split: str):
    if subset:
        return load_dataset(name, subset, split=split)
    return load_dataset(name, split=split)


def resolve_hub_model_id(args: argparse.Namespace) -> str | None:
    hub_id = (args.hub_model_id or os.environ.get("HUB_MODEL_ID") or "").strip()
    if hub_id:
        return hub_id
    if not args.push_to_hub or os.environ.get("SMOKE_TEST") == "1":
        return None
    if not os.environ.get("HF_TOKEN"):
        return None
    try:
        from huggingface_hub import whoami

        user = whoami().get("name")
        if user:
            return f"{user}/{args.run_name}"
    except Exception:
        pass
    return None


def main() -> None:
    args = parse_args()
    smoke_test = os.environ.get("SMOKE_TEST") == "1"
    output_dir = args.output_dir or str(DEFAULT_OUTPUT_ROOT / args.run_name)
    hub_model_id = resolve_hub_model_id(args)
    hub_push = bool(args.push_to_hub and hub_model_id and not smoke_test)

    setup_logging(args.run_name, output_dir if args.output_dir else None)

    if args.eval_only:
        logging.info("Eval-only mode: loading model from %s", args.eval_only)
        model = SentenceTransformer(args.eval_only)
        evaluator = NanoBEIREvaluator()
        with autocast_ctx():
            evaluator(model)
        return

    logging.info("Loading base model: %s", args.model)
    model = SentenceTransformer(
        args.model,
        model_card_data=SentenceTransformerModelCardData(
            language="en",
            license="apache-2.0",
            model_name=f"{args.model.split('/')[-1]} finetuned on {args.dataset}",
        ),
    )

    logging.info("Loading dataset: %s (%s)", args.dataset, args.subset)
    train_size = 50 if smoke_test else args.train_size
    eval_size = 20 if smoke_test else args.eval_size
    train_dataset = load_split(
        args.dataset, args.subset, args.train_split).select(range(train_size))
    eval_dataset = load_split(
        args.dataset, args.subset, args.eval_split).select(range(eval_size))
    if smoke_test:
        logging.info(
            "SMOKE_TEST=1: trimmed dataset; max_steps=1; skip Hub push")
    logging.info("  train: %s examples", f"{len(train_dataset):,}")
    logging.info("  eval:  %s examples", f"{len(eval_dataset):,}")

    loss = MultipleNegativesRankingLoss(model)
    evaluator = NanoBEIREvaluator()
    logging.info("Baseline evaluation (before training):")
    with autocast_ctx():
        baseline_eval = evaluator(model)[evaluator.primary_metric]
    metric_key = f"eval_{evaluator.primary_metric}"
    hub_kwargs = (
        {"push_to_hub": True, "hub_model_id": hub_model_id, "hub_strategy": "every_save"}
        if hub_push
        else {}
    )

    training_args = SentenceTransformerTrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,
        max_steps=1 if smoke_test else -1,
        per_device_train_batch_size=64 if torch.cuda.is_available() else 8,
        per_device_eval_batch_size=64 if torch.cuda.is_available() else 8,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_steps=0.1,
        lr_scheduler_type="linear",
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
        batch_sampler=BatchSamplers.NO_DUPLICATES,
        eval_strategy="steps",
        eval_steps=0.1,
        save_strategy="steps",
        save_steps=0.1,
        save_total_limit=2,
        logging_steps=0.01,
        logging_first_step=True,
        load_best_model_at_end=True,
        metric_for_best_model=metric_key,
        greater_is_better=True,
        report_to="none" if smoke_test else "trackio",
        run_name=args.run_name,
        seed=12,
        **hub_kwargs,
    )

    trainer = SentenceTransformerTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        loss=loss,
        evaluator=evaluator,
    )
    if not smoke_test:
        log_trackio_dashboard()
    trainer.train()

    logging.info("Post-training evaluation:")
    with autocast_ctx():
        score = evaluator(model)[evaluator.primary_metric]
    delta = score - baseline_eval
    verdict = "WIN" if delta >= 0.005 else "MARGINAL" if delta >= 0 else "REGRESSION"
    logging.info(
        "VERDICT: %s | score=%.4f | baseline=%.4f | delta=%+.4f",
        verdict,
        score,
        baseline_eval,
        delta,
    )

    final_dir = f"{output_dir}/final"
    model.save_pretrained(final_dir)
    logging.info("Saved final model to %s", final_dir)

    if smoke_test:
        logging.info("SMOKE_TEST=1: skipping Hub push")
        return
    if not hub_push:
        return

    try:
        commit_url = model.push_to_hub(hub_model_id)
        logging.info("Pushed model to %s", commit_url.rsplit("/commit/", 1)[0])
    except Exception:
        import traceback

        logging.error("Hub push failed:\n%s", traceback.format_exc())


if __name__ == "__main__":
    main()
