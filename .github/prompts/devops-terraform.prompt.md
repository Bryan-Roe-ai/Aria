```prompt
---
agent: agent
description: "Write Terraform infrastructure-as-code"
---
# Terraform IaC
## Task
Write Terraform configuration for infrastructure provisioning.
## Requirements
1. Define resources with proper naming. 2. Use modules for reusability.
3. Implement state management (remote backend). 4. Use variables and outputs.
5. Implement environment separation (dev/staging/prod).
## Constraints
- Remote state required. Lock state files. Plan before apply. Use workspaces or directories.
## Success Criteria
- Infrastructure provisioned consistently. State managed remotely. Environments isolated.
```
