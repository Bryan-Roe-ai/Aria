```prompt
---
agent: agent
description: "Implement secure CI/CD pipeline hardening"
---
# CI/CD Security
## Task
Harden CI/CD pipeline security.
## Requirements
1. Sign all artifacts and verify signatures. 2. Use ephemeral build environments.
3. Scan for secrets in source code (pre-commit). 4. Pin action versions by SHA.
5. Restrict deployment permissions.
## Constraints
- No long-lived secrets in CI. Use OIDC for cloud auth. Ephemeral runners preferred.
## Success Criteria
- Artifacts signed. No secrets leaked. Actions pinned. Deployments restricted.
```
