```prompt
---
agent: agent
description: "Implement secret management and rotation"
---
# Secret Management
## Task
Implement secure secret management and rotation.
## Requirements
1. Store secrets in vault (Azure Key Vault, HashiCorp Vault). 2. Never hardcode secrets in source code.
3. Rotate secrets on schedule (90 days). 4. Support zero-downtime rotation.
5. Audit secret access.
## Constraints
- Follow Aria convention: env vars or local.settings.json for local dev. Never commit secrets.
## Success Criteria
- No secrets in code. Rotation automated. Access audited. Zero-downtime rotation works.
```
