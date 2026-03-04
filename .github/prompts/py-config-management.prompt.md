```prompt
---
agent: agent
description: "Implement configuration management with YAML/JSON loading and validation"
---
# Config Management

## Task
Implement structured configuration loading with validation.

## Requirements
1. Load config from YAML, JSON, or TOML files.
2. Validate config against a schema (Pydantic or jsonschema).
3. Support config inheritance (base config + overrides).
4. Apply environment variable overrides on top.
5. Freeze config after loading to prevent runtime mutation.

## Constraints
- Config precedence: base file < override file < env vars.
- Fail fast on invalid config with specific error messages.
- Never commit secrets in config files.

## Success Criteria
- Config is validated and frozen at startup.
- Override hierarchy is respected.
- Invalid config produces actionable error messages.
```
