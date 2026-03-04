```prompt
---
agent: agent
description: "Implement database migration automation in deployments"
---
# Database Migration Automation
## Task
Automate database migrations in deployment pipeline.
## Requirements
1. Run migrations before application deployment. 2. Support forward and backward migrations.
3. Test migrations in staging first. 4. Handle migration failures with rollback.
5. Implement migration locking (no concurrent runs).
## Constraints
- Migrations must be backward-compatible. Test in staging. Lock during execution. Backup first.
## Success Criteria
- Migrations automated in pipeline. Backward-compatible. Tested in staging. Rollback works.
```
