```prompt
---
agent: agent
description: "Augment training data using data augmentation techniques"
---
# Data Augmentation

## Task
Augment an existing training dataset to improve model generalization.

## Context
- Augmenter: `lora/scripts/data_augmenter.py`
- Dataset analyzer: `lora/scripts/dataset_analyzer.py`
- Dataset preparation: `lora/scripts/prepare_dataset.py`
- Synthetic generation: `scripts/generate_synthetic_datasets.py`

## Requirements
1. Analyze the existing dataset with `dataset_analyzer.py` to understand distribution.
2. Choose augmentation strategies (paraphrase, noise, synonym replacement, etc.).
3. Run augmentation; preserve original data in a separate location.
4. Profile augmented data to verify quality and diversity.
5. Validate augmented data works with the training pipeline.

## Constraints
- Never modify original dataset files; write augmented data to separate output files.
- `datasets/` is read-only; write to `data_out/` or `lora/data/`.
- Preserve label integrity during augmentation.
- Document augmentation strategies and parameters used.

## Success Criteria
- Augmented dataset is larger and more diverse than the original.
- Data quality check passes without anomalies.
- Training on augmented data shows improvement or at least no regression.
- Augmentation is reproducible with documented parameters.
```
