```instructions
---
name: "Scripts-Orchestrators"
description: "Status-driven dry-run-first guidance for scripts/*.py orchestrators"
applyTo: "scripts/**/*.py"
---
# Orchestrator Scripts – Python

- Always support `--dry-run` for validation before full execution.
- Persist machine-readable status files under `data_out/<orchestrator>/status.json`.
- Follow config precedence: base YAML < CLI flags < per-job overrides < env vars.
- Treat `datasets/` as read-only inputs.
- Write generated artifacts and runtime state to `data_out/` only.
- Emit actionable errors with clear recovery hints.
- Keep orchestration idempotent where practical.
```
