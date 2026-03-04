```prompt
---
agent: agent
description: "Configure and run vision fine-tuning or multimodal training"
---
# Vision Training

## Task
Set up and execute a vision or multimodal training pipeline.

## Context
- Vision training: `scripts/train_vision.py`
- Evaluation: `scripts/evaluate_vision.py`
- Inference: `scripts/vision_inference.py`
- Avatar integration: `scripts/vision_avatar_integration.py`
- Visual expansion: `scripts/aria_visual_expansion.py`

## Requirements
1. Verify GPU/VRAM availability for vision models.
2. Prepare image/multimodal datasets (check `datasets/` for existing data).
3. Configure training parameters (batch size, epochs, learning rate).
4. Run training and monitor progress.
5. Evaluate with `scripts/evaluate_vision.py` against baselines.

## Constraints
- `datasets/` is read-only; write outputs to `data_out/`.
- Vision models require more VRAM — check with `scripts/vram_calculator.py`.
- Validate image data integrity before training.
- Never train on evaluation data.

## Success Criteria
- Training completes without OOM errors.
- Evaluation metrics meet acceptable thresholds.
- Outputs are saved to `data_out/` with proper naming.
- Inference produces reasonable results on test images.
```
