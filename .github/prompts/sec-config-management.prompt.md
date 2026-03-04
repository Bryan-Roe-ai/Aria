```prompt
---
agent: agent
description: "Implement secure configuration management"
---
# Secure Configuration
## Task
Implement secure configuration management practices.
## Requirements
1. Separate config from code. 2. Encrypt sensitive config values.
3. Validate config on startup (fail fast). 4. Support environment-specific overrides.
5. Audit config changes.
## Constraints
- Follow Aria config precedence: base YAML < CLI < per-job < env vars. Log config load (redacted).
## Success Criteria
- Config separated from code. Sensitive values encrypted. Validated on startup.
```
