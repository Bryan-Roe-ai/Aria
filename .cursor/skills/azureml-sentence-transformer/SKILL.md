---
name: azureml-sentence-transformer
description: Submit and troubleshoot Aria SentenceTransformer bi-encoder training on Azure ML (50k all-nli MNRL). Use when the user asks to train embeddings on Azure ML, submit job-sentence-transformer-train.yml, run the 50k MiniLM job, or wire ST training through Azure instead of HF Jobs or local GPU.
---

# Azure ML SentenceTransformer Training (Aria)

Fine-tune `all-MiniLM-L6-v2` on Azure ML GPU compute. Default job: **50k** `sentence-transformers/all-nli` triplets, MNRL loss, NanoBEIR eval.

## Repo map

| Path | Role |
|------|------|
| `ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml/job-sentence-transformer-train.yml` | Command job spec |
| `ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml/environment-sentence-transformer.yml` | Conda env for the job |
| `ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml/submit_sentence_transformer.sh` | Preferred submit wrapper |
| `ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml/submit_sentence_transformer_azureml.py` | Python submit wrapper (calls `az ml job create`) |
| `ai-projects/lora-training/microsoft_phi-silica-3.6_v1/scripts/train_sentence_transformer.py` | Training script (supports `--push-to-hub`, `--hub-model-id`) |
| `ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml/README.md` | §13 — full docs |
| `.github/workflows/azureml-train.yml` | Manual dispatch; set `jobFile` to the ST job YAML |

Documented defaults: `rg-phi36-ml`, `phi36-ml-workspace`, `azureml:gpu-cluster`.

## Prerequisites (verify before submit)

1. `az login` (or valid service principal / `AZURE_CREDENTIALS` in CI)
2. `az extension add -n ml`
3. Env vars set (not `__REPLACE__`):
   - `AZURE_ML_SUBSCRIPTION_ID`
   - `AZURE_ML_RESOURCE_GROUP` (default `rg-phi36-ml`)
   - `AZURE_ML_WORKSPACE` (default `phi36-ml-workspace`)
4. Optional Hub push: `HF_TOKEN` (write) + `HUB_MODEL_ID` (e.g. `Bryan-Roe-ai/aria-minilm-all-nli-50k`)

**Devcontainer note:** This repo often has no `az` on PATH and no Azure login. Install CLI if needed (`pip install azure-cli` in a venv), then authenticate. Do not assume submit succeeded without checking `az account show`.

## Submit workflow

```bash
export AZURE_ML_SUBSCRIPTION_ID="<subscription-id>"
export AZURE_ML_RESOURCE_GROUP="rg-phi36-ml"
export AZURE_ML_WORKSPACE="phi36-ml-workspace"
export HF_TOKEN="<optional-write-token>"
export HUB_MODEL_ID="Bryan-Roe-ai/aria-minilm-all-nli-50k"

cd ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml
./submit_sentence_transformer.sh
```

**Smoke on Azure** (cheap validation):

```bash
TRAIN_SIZE=512 EVAL_SIZE=128 ./submit_sentence_transformer.sh
```

**GitHub Actions:** workflow_dispatch **AzureML LoRA Train** with  
`jobFile=ai-projects/lora-training/microsoft_phi-silica-3.6_v1/azureml/job-sentence-transformer-train.yml`  
(requires `AZURE_CREDENTIALS` repo/org secret).

## After submit

```bash
az ml job show -n <JOB_NAME>
az ml job stream -n <JOB_NAME>
az ml job download -n <JOB_NAME> --output-name model_out --download-path ./st_model_out
```

Artifacts: `model_out/final/` on the job output mount. MLflow tracking: `azureml://tracking`.

## Local alternatives (when Azure blocked)

| Path | When |
|------|------|
| `SMOKE_TEST=1 python scripts/train_sentence_transformer.py` | Local CPU/GPU smoke (no Hub push) |
| HF Jobs via `hf_jobs` MCP | User has HF Jobs credits; ephemeral — use `hub_strategy=every_save` |
| Full local run | Machine with GPU + `sentence-transformers[train]` |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Please run az login` | No Azure session | `az login` or device code |
| `subscription ... doesn't exist` | Wrong ID or wrong tenant | `az account list`, set correct subscription |
| `Set AZURE_ML_SUBSCRIPTION_ID` | Placeholder `.env` | Export real values; never commit secrets |
| Job fails on `--push-to-hub` | Missing `HF_TOKEN` in job env | Pass `environment_variables.HF_TOKEN` at submit |
| OOM on GPU | Batch 64 too large | Override `per_device_train_batch_size` in training script or use larger VM |
| HF Jobs 402 | Insufficient HF credits | Use Azure ML path instead |

## Agent checklist

- [ ] Confirm `job-sentence-transformer-train.yml` exists on the branch being submitted
- [ ] Confirm training script has `--push-to-hub` / `--hub-model-id` if job command uses them
- [ ] Verify auth (`az account show`) before claiming submit success
- [ ] Prefer `submit_sentence_transformer.sh` over re-inventing `az ml job create` flags
- [ ] Report job name + Studio URL after successful submit
