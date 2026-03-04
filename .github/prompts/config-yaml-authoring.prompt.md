```prompt
---
agent: agent
description: "Design or modify a YAML config for orchestrators, training, quantum, or evaluation"
---
# Config YAML Authoring

## Task
Create or update a YAML configuration file for an Aria orchestrator or pipeline.

## Context
- Config directory: `config/` with subdirectories `training/`, `quantum/`, `evaluation/`
- Orchestrators: `scripts/autotrain.py`, `scripts/quantum_autorun.py`, `scripts/evaluation_autorun.py`
- Master config: `config/master_orchestrator.yaml`

## Requirements
1. Use lowercase `snake_case` keys throughout.
2. Include inline YAML comments for non-obvious fields.
3. Set safe defaults: `dry_run: true`, `simulator: local`, conservative `epochs` and `batch_size`.
4. Follow config precedence: base YAML < CLI flags < per-job overrides < env vars.
5. Validate against the orchestrator's expected schema (dry-run).

## Constraints
- Never embed secrets in config files; reference env var names (e.g., `api_key: ${AZURE_KEY}`).
- Keep defaults conservative to prevent accidental expensive runs.
- Service configs (systemd units) must be minimal and well-commented.

## Success Criteria
- Config is valid YAML that parses without errors.
- Orchestrator `--dry-run` passes with the new config.
- All keys are documented with comments.
```
