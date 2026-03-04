```instructions
---
name: "Config-YAML"
description: "Guidance for config/ YAML and JSON configuration files"
applyTo: "config/**"
---
# Config Files

- `config/` holds YAML and JSON configuration for orchestrators, training, quantum, evaluation, and system services.
- Subdirectories: `training/` (LoRA/autotrain jobs), `quantum/` (quantum autorun jobs), `evaluation/` (eval configs).
- Config precedence: base YAML < CLI flags < per-job YAML overrides < environment variables.
- YAML conventions:
  - Use lowercase snake_case keys.
  - Include comments for non-obvious fields.
  - Keep defaults safe (e.g., `dry_run: true`, `simulator: local`, small `epochs`/`batch_size`).
- JSON configs (`azure_monitor_alerts.json`, `notification_config.yaml`): keep schemas flat and documented.
- Never embed secrets in config files; reference env var names instead (e.g., `api_key: ${AZURE_KEY}`).
- Validate config against expected schema before orchestrator execution; fail fast with clear messages.
- Service configs (`aria_automation.service`): keep systemd unit files minimal and well-commented.
```
