```prompt
---
agent: agent
description: "Configure and execute a LoRA training run end-to-end"
---
# LoRA Training Run

## Task
Configure, validate, and execute a LoRA adapter training run.

## Context
- Training orchestrator: `scripts/autotrain.py`
- Job configs: `config/training/`
- Evaluation: `scripts/evaluate_lora_model.py`, `scripts/evaluate_model.py`
- Promotion: `scripts/train_and_promote.py`
- VRAM calculator: `scripts/vram_calculator.py`

## Requirements
1. Verify hardware prerequisites (GPU, VRAM) using `scripts/vram_calculator.py`.
2. Create or update job YAML in `config/training/`.
3. Dry-run first: `python scripts/autotrain.py --dry-run`.
4. Execute training and monitor progress.
5. Evaluate the trained adapter against a baseline.
6. Confirm adapter readiness: both `adapter_config.json` and `adapter_model.safetensors` must exist.

## Constraints
- Config precedence: base YAML < CLI flags < per-job overrides < env vars.
- `datasets/` is read-only; training outputs go to `data_out/`.
- Never train on evaluation data.
- Respect VRAM limits; choose batch size accordingly.

## Success Criteria
- Dry-run passes without errors.
- Training completes and produces valid adapter files.
- Evaluation metrics meet or exceed baseline thresholds.
- Status file updated in `data_out/autotrain/status.json`.
```
