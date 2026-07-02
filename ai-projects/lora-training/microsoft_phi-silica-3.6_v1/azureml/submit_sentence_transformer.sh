#!/usr/bin/env bash
# Submit the 50k SentenceTransformer training job to Azure ML.
#
# Prerequisites:
#   az login
#   az extension add -n ml
#   az account set --subscription "$AZURE_ML_SUBSCRIPTION_ID"
#   az configure --defaults group="$AZURE_ML_RESOURCE_GROUP" workspace="$AZURE_ML_WORKSPACE"
#
# Usage:
#   export AZURE_ML_SUBSCRIPTION_ID=...
#   export AZURE_ML_RESOURCE_GROUP=...
#   export AZURE_ML_WORKSPACE=...
#   export HF_TOKEN=...          # optional; enables Hub push
#   ./submit_sentence_transformer.sh
#
# Optional overrides:
#   COMPUTE=azureml:gpu-cluster
#   HUB_MODEL_ID=Bryan-Roe-ai/aria-minilm-all-nli-50k
#   TRAIN_SIZE=50000
#   STREAM=1                       # stream logs (default)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JOB_FILE="${SCRIPT_DIR}/job-sentence-transformer-train.yml"
COMPUTE="${COMPUTE:-azureml:gpu-cluster}"
TRAIN_SIZE="${TRAIN_SIZE:-50000}"
EVAL_SIZE="${EVAL_SIZE:-1000}"
RUN_NAME="${RUN_NAME:-aria-minilm-all-nli-50k}"
HUB_MODEL_ID="${HUB_MODEL_ID:-}"
STREAM="${STREAM:-1}"

: "${AZURE_ML_SUBSCRIPTION_ID:?Set AZURE_ML_SUBSCRIPTION_ID}"
: "${AZURE_ML_RESOURCE_GROUP:?Set AZURE_ML_RESOURCE_GROUP}"
: "${AZURE_ML_WORKSPACE:?Set AZURE_ML_WORKSPACE}"

az account set --subscription "$AZURE_ML_SUBSCRIPTION_ID"
az configure --defaults group="$AZURE_ML_RESOURCE_GROUP" workspace="$AZURE_ML_WORKSPACE"

SET_ARGS=(
  "compute=${COMPUTE}"
  "inputs.train_size=${TRAIN_SIZE}"
  "inputs.eval_size=${EVAL_SIZE}"
  "inputs.run_name=${RUN_NAME}"
  "inputs.hub_model_id=${HUB_MODEL_ID}"
)

if [[ -n "${HF_TOKEN:-}" ]]; then
  SET_ARGS+=("environment_variables.HF_TOKEN=${HF_TOKEN}")
fi

echo "Submitting ${JOB_FILE} (train_size=${TRAIN_SIZE}, compute=${COMPUTE})"

if [[ "${STREAM}" == "1" ]]; then
  az ml job create -f "$JOB_FILE" --set "${SET_ARGS[@]}" --stream
else
  az ml job create -f "$JOB_FILE" --set "${SET_ARGS[@]}"
fi
