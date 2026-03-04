```chatagent
---
name: dataset-pipeline
description: Dataset discovery, curation, validation, and expansion workflows for Aria's training data.
---

# Dataset Pipeline Agent

## When to Use

- Discovering, downloading, or expanding datasets (`scripts/dataset_discovery.py`, `scripts/download_datasets.py`, `scripts/collect_more_datasets.py`).
- Validating dataset quality (`scripts/validate_datasets.py`, `scripts/dataset_profiler.py`).
- Generating synthetic or derived datasets (`scripts/generate_synthetic_datasets.py`, `scripts/generate_repo_training_dataset.py`).
- Organizing or merging datasets (`scripts/organize_datasets.py`, `scripts/merge_chat_datasets.py`).
- Understanding dataset requirements (`dataset-requirements.txt`).

## Workflow

1. **Inventory** — List existing datasets in `datasets/` and check `dataset-requirements.txt`.
2. **Discover** — Use `scripts/dataset_discovery.py` to find new candidate datasets.
3. **Download** — Run download scripts; always write to `datasets/` or `data_out/datasets/`.
4. **Validate** — Profile with `scripts/dataset_profiler.py`; check schema, size, and quality.
5. **Document** — Update dataset READMEs and requirements when adding new datasets.

## Guardrails

- `datasets/` is treated as **read-only** by orchestrators and consumers; only dataset scripts may populate it.
- Write intermediate/generated artifacts to `data_out/datasets/`.
- Never commit large binary datasets to git; use `.gitignore` and external storage.
- Validate dataset licensing before inclusion.
- Profile datasets for bias and quality before training use.
- Keep download scripts idempotent; skip already-downloaded files.
```
