```prompt
---
agent: agent
description: "Implement environment promotion workflow (dev→staging→prod)"
---
# Environment Promotion
## Task
Implement environment promotion workflow.
## Requirements
1. Define environment hierarchy (dev → staging → prod). 2. Promote artifacts between environments.
3. Run environment-specific tests at each stage. 4. Gate promotion with approvals.
5. Maintain environment parity.
## Constraints
- Same artifact across all environments. Config differs, code doesn't. Approval for prod.
## Success Criteria
- Same artifact promoted through environments. Tests pass at each stage. Approvals enforced.
```
