```prompt
---
agent: agent
description: "Discover, download, validate, or expand training datasets"
---
# Dataset Curation

## Task
Curate training data: discover new sources, download, validate quality, and organize.

## Context
- Discovery: `scripts/dataset_discovery.py`, `scripts/download_datasets.py`
- Validation: `scripts/validate_datasets.py`, `scripts/dataset_profiler.py`
- Generation: `scripts/generate_synthetic_datasets.py`, `scripts/generate_repo_training_dataset.py`
- Merge/organize: `scripts/organize_datasets.py`, `scripts/merge_chat_datasets.py`
- Requirements: `dataset-requirements.txt`

## Requirements
1. Identify candidate datasets matching project requirements.
2. Download idempotently (skip existing files).
3. Profile for schema, size, quality, and potential bias.
4. Organize into the correct `datasets/` subdirectory.
5. Update `dataset-requirements.txt` or dataset READMEs as needed.

## Constraints
- `datasets/` is treated as read-only by orchestrators; only dataset scripts may populate it.
- Never commit large binaries to git.
- Validate licensing before inclusion.
- Write intermediate artifacts to `data_out/datasets/`.

## Success Criteria
- New data is downloaded, validated, and correctly organized.
- Profiling report shows acceptable quality metrics.
- No orchestrator or training scripts are broken by the new data.
```
