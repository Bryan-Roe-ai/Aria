```prompt
---
agent: agent
description: "Implement secrets management in CI/CD"
---
# CI/CD Secrets
## Task
Manage secrets securely in CI/CD pipelines.
## Requirements
1. Store secrets in vault (GitHub Secrets, Azure Key Vault). 2. Inject secrets at runtime, not build time.
3. Mask secrets in logs. 4. Rotate secrets without pipeline changes.
5. Audit secret access.
## Constraints
- Never store secrets in code or Docker images. Use OIDC for cloud auth. Rotate quarterly.
## Success Criteria
- Secrets injected at runtime. Masked in logs. Rotatable without code changes.
```
