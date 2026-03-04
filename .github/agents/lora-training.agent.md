```chatagent
---
name: lora-training
description: LoRA adapter training, evaluation, promotion, and deployment workflows.
---

# LoRA Training Agent

## When to Use

- Running or configuring LoRA adapter training (`scripts/autotrain.py`, training configs).
- Evaluating trained models (`scripts/evaluate_lora_model.py`, `scripts/evaluate_model.py`).
- Promoting or deploying adapters (`scripts/train_and_promote.py`, `scripts/model_deployer.py`).
- Vision fine-tuning (`scripts/train_vision.py`, `scripts/evaluate_vision.py`).
- Training pipeline automation (`scripts/automated_training_pipeline.py`).

## Workflow

1. **Check prerequisites** — Verify GPU/VRAM with `scripts/vram_calculator.py`; ensure datasets are ready.
2. **Configure** — Edit job YAML in `config/training/`; follow config precedence (base YAML < CLI < per-job overrides < env vars).
3. **Dry-run** — Run `python scripts/autotrain.py --dry-run` to validate config.
4. **Train** — Execute training; monitor via dashboard or `scripts/monitor_training.ps1`.
5. **Evaluate** — Run evaluation scripts; compare metrics against baselines.
6. **Validate adapter** — Confirm both `adapter_config.json` and `adapter_model.safetensors` exist.
7. **Promote** — Use promotion scripts to deploy validated adapters.

## Guardrails

- Treat `datasets/` as read-only; write training outputs to `data_out/`.
- Always dry-run before real training; avoid wasting GPU time on bad configs.
- LoRA adapters are valid only when both `adapter_config.json` and `adapter_model.safetensors` exist.
- Monitor VRAM usage; respect hardware limits.
- Log training metrics for reproducibility; persist to `data_out/<job>/`.
- Never train on test/evaluation data.
```
