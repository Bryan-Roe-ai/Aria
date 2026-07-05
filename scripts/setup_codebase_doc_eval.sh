#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/setup_codebase_doc_eval.sh [model_deployment_name] [dataset_path_optional]
#
# Defaults are discovered from workspace context provided by the user.

ENV_NAME="codebase-doc-eval"
PROJECT_ENDPOINT="https://admin-6701-resource.services.ai.azure.com/api/projects/admin-6701"
AGENT_NAME="codebase-documentation-generator"
AGENT_KIND="prompt"
MODEL_DEPLOYMENT_NAME="${1:-gpt-5.3-codex}"
DATASET_PATH="${2:-}"

if ! command -v azd >/dev/null 2>&1; then
  echo "ERROR: azd is not installed or not on PATH."
  echo "Install azd, then rerun this script."
  exit 127
fi

cd "$(dirname "$0")/.."

# Ensure azd project marker exists (required by user instructions)
if [[ ! -f azure.yaml ]]; then
  cat > azure.yaml <<'YAML'
name: codebase-documentation-generator-eval
YAML
fi

# Create/select env and set required values
if ! azd env list | grep -q "${ENV_NAME}"; then
  azd env new "${ENV_NAME}"
else
  azd env select "${ENV_NAME}"
fi

azd env set AZURE_AI_PROJECT_ENDPOINT "${PROJECT_ENDPOINT}"
azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME "${MODEL_DEPLOYMENT_NAME}"

# Optional compatibility alias used by some projects
azd env set FOUNDRY_PROJECT_ENDPOINT "${PROJECT_ENDPOINT}"

# Show env values for traceability
azd env get-values

# Evaluate setup (option a from deploy skill guidance)
# - If dataset is provided, reuse it
# - Otherwise, generate synthetic Q&A from agent purpose/instructions
if [[ -n "${DATASET_PATH}" ]]; then
  azd ai agent eval generate \
    --name "${AGENT_NAME}" \
    --dataset "${DATASET_PATH}" \
    --eval-model "${MODEL_DEPLOYMENT_NAME}" \
    --no-wait --no-prompt
else
  azd ai agent eval generate \
    --name "${AGENT_NAME}" \
    --gen-instruction "Assist users by generating clear, accurate codebase documentation from source repositories, including architecture overviews, setup guides, API references, and file-level summaries." \
    --eval-model "${MODEL_DEPLOYMENT_NAME}" \
    --no-wait --no-prompt
fi

# Run the generated suite
azd ai agent eval run --name "${AGENT_NAME}" --no-prompt

echo "Evaluation setup and run completed for ${AGENT_NAME}."
echo "Agent kind: ${AGENT_KIND}"
