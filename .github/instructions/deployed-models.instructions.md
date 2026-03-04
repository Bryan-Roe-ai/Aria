```instructions
---
name: "Deployed-Models"
description: "Guidance for deployed_models/ model registry and versioned artifact management"
applyTo: "deployed_models/**"
---
# Deployed Models

- `deployed_models/` stores production-deployed model artifacts and the model registry.
- `model_registry.json` is the source of truth for deployed versions, timestamps, and quality metrics.
- Never overwrite a deployed model without creating a backup first.
- Deployment done via `scripts/model_deployer.py`; don't manually copy files into this directory.
- Each deployed version should have: adapter files, config, deployment metadata, and quality gate results.
- LoRA adapters need both `adapter_config.json` and `adapter_model.safetensors` to be valid.
- Keep this directory outside training pipelines; only the deployer writes here.
- Rollback means pointing to a previous version entry in the registry, not deleting files.
```
