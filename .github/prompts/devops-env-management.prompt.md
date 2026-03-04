```prompt
---
agent: agent
description: "Implement environment variable management across environments"
---
# Environment Management
## Task
Manage environment variables across deployment environments.
## Requirements
1. Define env vars per environment in config. 2. Validate required vars on startup.
3. Document all env vars with descriptions. 4. Support defaults for optional vars.
5. Encrypt sensitive values.
## Constraints
- Never hardcode env-specific values. Use env var groups. Document defaults.
## Success Criteria
- Env vars managed per environment. Validated on startup. Documented. Encrypted.
```
