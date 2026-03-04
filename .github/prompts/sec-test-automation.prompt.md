```prompt
---
agent: agent
description: "Implement security testing automation in CI"
---
# Security Test Automation
## Task
Automate security testing in CI pipeline.
## Requirements
1. Run SAST on every PR. 2. Run DAST on staging deployments.
3. Run dependency vulnerability scan daily. 4. Run secrets detection pre-commit.
5. Generate security test reports.
## Constraints
- Block PRs with critical findings. Report medium/low as warnings. Secrets detection in pre-commit hook.
## Success Criteria
- Security tests run automatically. Critical findings blocked. Reports generated. Secrets caught.
```
