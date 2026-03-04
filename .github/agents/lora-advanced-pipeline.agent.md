```chatagent
---
name: lora-advanced-pipeline
description: Advanced LoRA pipeline scripts including RAG, DeepSpeed, data augmentation, model serving, and metrics.
---

# LoRA Advanced Pipeline Agent

## When to Use

- Setting up RAG pipelines with LoRA adapters (`lora/scripts/rag_pipeline.py`).
- Configuring DeepSpeed Zero-3 distributed training (`lora/scripts/deepspeed_zero3.json`).
- Data augmentation for training datasets (`lora/scripts/data_augmenter.py`).
- Serving trained models (`lora/scripts/model_server.py`).
- GPU optimization (`lora/scripts/gpu_optimizer.py`), learning rate finding (`lr_finder.py`).
- Semantic pruning (`lora/scripts/semantic_pruning.py`), dataset analysis, metrics logging.
- OTel/observability callbacks (`lora/scripts/otel_callback.py`).

## Workflow

1. **Prepare data** — Use `prepare_dataset.py` and `data_augmenter.py` to ready training data.
2. **Analyze** — Run `dataset_analyzer.py` to profile data quality and distribution.
3. **Find LR** — Use `lr_finder.py` to determine optimal learning rate.
4. **Configure** — Set up DeepSpeed config in `deepspeed_zero3.json` if distributed.
5. **Train** — Run `train_lora.py` or `run_pipeline.py` with monitoring via `training_monitor.py`.
6. **Evaluate** — Check metrics via `metrics_logger.py` and `auto_eval.py`.
7. **Serve** — Deploy using `model_server.py` or `model_exporter.py`.

## Guardrails

- DeepSpeed: validate config JSON before launching distributed training.
- GPU optimizer: respect VRAM limits; use `scripts/vram_calculator.py` first.
- RAG pipeline: ensure vector store is initialized before querying.
- Model server: bind to localhost by default; require explicit flag for network exposure.
- OTel callback: keep spans lightweight; don't log PII or model weights.
- Data augmentation: preserve original data; write augmented output to separate files.
```
