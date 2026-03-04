```prompt
---
agent: agent
description: "Configure DeepSpeed Zero-3 for distributed LoRA training"
---
# DeepSpeed Training

## Task
Configure and launch distributed LoRA training using DeepSpeed Zero-3.

## Context
- DeepSpeed config: `lora/scripts/deepspeed_zero3.json`
- Training script: `lora/scripts/train_lora.py`, `lora/scripts/run_pipeline.py`
- GPU optimizer: `lora/scripts/gpu_optimizer.py`
- VRAM calculator: `scripts/vram_calculator.py`

## Requirements
1. Calculate VRAM requirements with `scripts/vram_calculator.py`.
2. Configure `deepspeed_zero3.json` for available GPU count and memory.
3. Set appropriate batch size, gradient accumulation, and offload settings.
4. Launch training with DeepSpeed integration.
5. Monitor GPU utilization and training progress.

## Constraints
- Validate DeepSpeed config JSON before launching.
- Respect VRAM limits; use CPU offload if needed.
- Write all outputs to `data_out/`.
- Test on a small batch first before full run.

## Success Criteria
- DeepSpeed config is valid and optimized for available hardware.
- Training launches without OOM errors.
- GPU utilization is balanced across devices.
- Training converges and produces valid adapter files.
```
