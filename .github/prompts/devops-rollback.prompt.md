```prompt
---
agent: agent
description: "Implement rollback automation for failed deployments"
---
# Rollback Automation
## Task
Automate rollback for failed deployments.
## Requirements
1. Detect deployment failure (health check, error rate). 2. Trigger automatic rollback to previous version.
3. Restore previous configuration. 4. Notify team of rollback.
5. Post-rollback validation.
## Constraints
- Rollback within 5 minutes. Keep N previous versions. Validate after rollback.
## Success Criteria
- Failed deployments roll back automatically. Previous version restored. Team notified.
```
