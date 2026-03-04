```prompt
---
agent: agent
description: "Deploy a trained model with quality gates, strategy selection, and rollback plan"
---
# Model Deploy

## Task
Deploy a trained model through quality gates with a safe deployment strategy.

## Context
- Deployer: `scripts/model_deployer.py`
- Registry: `deployed_models/model_registry.json`
- Quality gate metrics: accuracy, loss thresholds
- Strategies: canary, blue-green, rolling

## Requirements
1. Scan for candidates: `python scripts/model_deployer.py --scan`.
2. Validate quality gates pass for the target model.
3. Choose deployment strategy (default: canary for production).
4. Execute deployment with rollback plan documented.
5. Verify post-deployment via `/api/ai/status` and dashboard.

## Constraints
- Never deploy without passing quality gates.
- Both `adapter_config.json` and `adapter_model.safetensors` must exist.
- Log deployment to model registry with timestamp and version.

## Success Criteria
- Model deployed successfully with chosen strategy.
- Registry updated with new version entry.
- Rollback procedure documented and tested.
- `/api/ai/status` shows healthy after deployment.
```
