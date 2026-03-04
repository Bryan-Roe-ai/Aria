```chatagent
---
name: model-deployment
description: Model quality gating, scoring, deployment strategies, rollback, and registry management.
---

# Model Deployment Agent

## When to Use

- Deploying trained models via `scripts/model_deployer.py`.
- Configuring quality gates (accuracy/loss thresholds).
- Choosing deployment strategies (canary, blue-green, rolling).
- Managing the model registry (`deployed_models/model_registry.json`).
- Rolling back a failed deployment.

## Workflow

1. **Scan** — `python scripts/model_deployer.py --scan` to find deployable models.
2. **Validate gates** — Check quality thresholds before promotion.
3. **Deploy** — `python scripts/model_deployer.py --deploy best --strategy canary`.
4. **Monitor** — Watch `/api/ai/status` and dashboard metrics post-deploy.
5. **Rollback** — `python scripts/model_deployer.py --rollback <version>` if issues appear.

## Guardrails

- Never deploy without passing quality gates.
- Prefer canary strategy for production to limit blast radius.
- Keep `deployed_models/model_registry.json` as the source of truth for versions.
- Log all deployments and rollbacks with timestamps.
- Validate adapter readiness (both `adapter_config.json` and `adapter_model.safetensors`).
```
