# Automated Multi-Model Training Pipeline

This document explains the usage of `scripts/automated_training_pipeline.py`, a high-level orchestration wrapper for rapid LoRA experimentation across supported base models (currently `phi` and `qwen`). It unifies synthetic dataset generation, conditional training, ranking, cleanup, and Azure ML job spec emission.

---

## Why Use This Wrapper?

* One command drives multi-model synthetic data generation + (optional) LoRA training.
* Consistent summary artifacts for downstream dashboards & CI.
* Seamless edge cases: generate-only, cleanup, evaluation disable.
* Turn-key Azure ML remote execution spec without manual YAML authoring.
* Append-only historical lineage maintained separately by `parallel_train.py` (`data_out/parallel_training/status.json`).

---

## Core Outputs

| Artifact | Location | Purpose |
|----------|----------|---------|
| Summary JSON | `data_out/automated_training/summary_<run_label>.json` | Aggregated results for this wrapper invocation (per model). |
| Azure ML Job Spec (optional) | `.azureml/job_<run_label>.yaml` | Ready for `az ml job create --file` remote submission. |
| Conda Environment Definition | `.azureml/environment.yml` | Base environment for Azure ML job. Generated if missing or forced. |
| Synthetic Dataset | `datasets/chat/auto_generated/` | Train/Test JSON/JSONL for quick experiments. |
| Status History | `data_out/parallel_training/status.json` | Long-term cumulative log from underlying training script(s). |

---

## Key Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--models phi,qwen` | Comma list of models to process. | `phi,qwen` |
| `--quick` | Generate ~100 samples (fast dev mode). Ignored if `--samples` specified. | Off |
| `--samples <N>` | Override synthetic sample count. | None |
| `--generate-only` | Create synthetic dataset but skip training entirely. | Off |
| `--no-eval` | Skip evaluation & sample generation in underlying training. | Off |
| `--cleanup` | Remove intermediate checkpoints after successful training. | Off |
| `--ranking-metric perplexity_improvement / post_perplexity` | Controls ranking metric selection. | `perplexity_improvement` |
| `--min-train-samples <N>` | Skip training if train sample count below threshold. | 50 |
| `--output-name <str>` | Custom label replacing timestamp-based run label. | Auto timestamp |
| `--azure-ml-spec` | Emit Azure ML job spec + environment file. | Off |
| `--azure-ml-compute <cluster>` | Target compute cluster name for AML job. | `cpu-cluster` |
| `--azure-ml-experiment <name>` | AML experiment name. | `lora-autotrain` |
| `--azure-ml-env-name <name>` | Conda environment logical name. | `auto-training-env` |
| `--azure-ml-image <image>` | Base container image for AML. | `mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04` |
| `--force-azure-ml` | Overwrite existing environment.yml even if present. | Off |

---

## Typical Workflows

### 1. Quick Multi-Model Training (default models)

```powershell
python .\scripts\automated_training_pipeline.py --quick
```

Produces synthetic data (~100 requested → final ~63 train, 7 test) and trains both models (unless below `--min-train-samples`). Summary generated.

### 2. Generate Data Only (No Training)

```powershell
python .\scripts\automated_training_pipeline.py --generate-only --quick --models phi,qwen
```

Creates synthetic dataset. Summary file marks each model with `training_skipped: true`.

### 3. Targeted Single Model With Cleanup

```powershell
python .\scripts\automated_training_pipeline.py --models phi --samples 300 --cleanup
```

Generates 300 samples, trains phi LoRA, evaluates (unless `--no-eval`), ranks job(s), then removes intermediate checkpoints preserving adapter weights & metrics.

### 4. Ranking by Post-Perplexity

```powershell
python .\scripts\automated_training_pipeline.py --ranking-metric post_perplexity --quick
```

Ranking uses absolute post-training perplexity (lower is better) instead of improvement delta.

### 5. Skip Evaluation Entirely

```powershell
python .\scripts\automated_training_pipeline.py --no-eval --quick
```

Training still occurs; evaluation block omitted from status entry.

### 6. Emit Azure ML Spec (Generate Only)

```powershell
python .\scripts\automated_training_pipeline.py --azure-ml-spec --generate-only --quick --models phi,qwen
```

Generates synthetic data, writes summary, emits:
 
* `.azureml/environment.yml`
* `.azureml/job_<run_label>.yaml`


Command inside job YAML includes `--generate-only` (training will be skipped remotely as well).

### 7. Full Remote Spec (Train + Cleanup)

```powershell
python .\scripts\automated_training_pipeline.py --azure-ml-spec --cleanup --quick --models phi
```

Job spec command will run training (no `--generate-only` flag unless specified) and perform cleanup stage.

---

## Azure ML Submission Guide (Manual)

1. Ensure Azure CLI & ML extension installed:

```powershell
az extension add -n ml
```

1. Fill in Azure ML placeholders in `.env` (added automatically if missing):
   * `AZURE_ML_SUBSCRIPTION_ID`
   * `AZURE_ML_RESOURCE_GROUP`
   * `AZURE_ML_WORKSPACE`
   * Confirm `AZURE_ML_COMPUTE_TARGET` matches existing cluster.

1. Log in & set defaults:

```powershell
az login
az account set --subscription <SUBSCRIPTION_ID>
az configure --defaults group=<RESOURCE_GROUP> workspace=<WORKSPACE_NAME>
```

1. (Optional) Create or update environment:

```powershell
az ml environment create --file .azureml\environment.yml
```

1. Submit job:

```powershell
az ml job create --file .azureml\job_<run_label>.yaml
```

1. Monitor:

```powershell
az ml job show --name automated-training-<run_label>
az ml job stream --name automated-training-<run_label>
```

> Note: The generated job YAML intentionally omits `--azure-ml-spec` to prevent nested spec emission during remote execution.

---

## Summary JSON Structure

Minimal example (generate-only, truncated):

```json
{
  "run_label": "multi_<timestamp>",
  "models": ["phi", "qwen"],
  "generate_only": true,
  "runs": [
    {
      "model": "phi",
      "run_id": null,
      "training_skipped": true,
      "jobs": [{"status": "skipped", "dataset_train_samples": 63}]
    }
  ]
}
```

For training runs `run_id` links to the underlying last entry in `data_out/parallel_training/status.json` with detailed evaluation + ranking info.

---

## Internal Mechanics

* Synthetic dataset creation delegates to `scripts/auto_data_train.py` with `--train-mode none` when generate-only.
* Training & evaluation wrapper logic lives in `scripts/parallel_train.py`; wrapper only reads latest status entry.
* Ranking metrics:
  * `perplexity_improvement` = (pre - post) / pre (higher better)
  * `post_perplexity` = final perplexity (lower better)
* Cleanup removes large checkpoint directories while preserving adapter artifacts.

---

## Extending

1. Add new base model key (e.g. `mistral`) to `valid_models` set and implement branch logic in `auto_data_train.py`.
2. Introduce additional ranking metric → update `parallel_train.py` ranking computation and CLI choices.
3. Additional cloud target (e.g. Azure Batch) → new spec emission function following pattern of `emit_azure_ml_spec`.

---

## Troubleshooting

| Symptom | Cause | Resolution |
|---------|-------|-----------|
| No job YAML produced | Forgot `--azure-ml-spec` flag | Re-run with flag. |
| Job spec command trains unexpectedly | Omitted `--generate-only` in original invocation | Add `--generate-only` and regenerate spec. |
| AML job fails environment solve | Missing dependency versions | Add pinned versions to `environment.yml` & re-run with `--force-azure-ml`. |
| Skipped training due to samples | `--min-train-samples` threshold | Lower threshold or increase `--samples`. |
| Ranking field null | Generate-only or evaluation disabled | Perform real training with evaluation enabled. |

---

## Recommended Next Steps

* Add CI step to validate generated YAML schema with `az ml job validate` (future).
* Integrate summary ingestion into dashboard view.
* Expand synthetic recipe diversity for robustness.

---

## Version & Maintenance

Last updated: 2025-11-25  
Script path: `scripts/automated_training_pipeline.py`  
Maintain consistency with project instructions in `copilot-instructions.md` for dataset immutability & output conventions.

---

Happy automating! ⚙️
