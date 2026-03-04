```prompt
---
agent: agent
description: "Implement database connection string management"
---
# Connection String Management
## Task
Manage database connection strings securely.
## Requirements
1. Store connection strings in Key Vault or env vars. 2. Support connection string rotation.
3. Use managed identity when available. 4. Configure connection parameters (timeout, pool, encrypt).
5. Different connection strings per environment.
## Constraints
- Follow Aria convention: env vars or local.settings.json. Never hardcode. Use managed identity.
## Success Criteria
- Connection strings secure. Rotation works. Managed identity used. Per-environment config.
```
