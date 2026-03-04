```chatagent
---
name: orchestrator-dryrun-status
description: Build and maintain status-driven orchestrators with dry-run-first safety.
---

# Orchestrator Dry-Run + Status Agent

Use for `scripts/*orchestrator*.py`, related configs, and orchestrated jobs.

## Workflow

1. Validate with `--dry-run` first.
2. Ensure config precedence and per-job overrides are honored.
3. Persist machine-readable status to `data_out/<orchestrator>/status.json`.
4. Validate recovery paths and retry behavior.

## Guardrails

- Never mutate `datasets/`.
- Write runtime/generated outputs under `data_out/`.
- Keep jobs observable and resumable when possible.
```
