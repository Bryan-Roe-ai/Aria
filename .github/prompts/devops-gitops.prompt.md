```prompt
---
agent: agent
description: "Implement GitOps workflow for declarative deployments"
---
# GitOps Workflow
## Task
Implement GitOps for declarative infrastructure and deployments.
## Requirements
1. Store all config in Git (single source of truth). 2. Use ArgoCD or Flux for reconciliation.
3. Automate sync from Git to cluster. 4. Handle drift detection and correction.
5. Implement approval workflows for production.
## Constraints
- Git is source of truth. No manual changes to cluster. Audit all changes via Git history.
## Success Criteria
- All changes via Git. Auto-sync works. Drift corrected. Audit trail in Git.
```
