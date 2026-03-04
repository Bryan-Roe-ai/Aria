```prompt
---
agent: agent
description: "Implement strangler fig pattern for legacy migration"
---
# Strangler Fig Migration
## Task
Migrate from legacy system using strangler fig pattern.
## Requirements
1. Route new features to new system. 2. Gradually migrate old features.
3. Run both systems in parallel. 4. Verify parity between old and new.
5. Decommission old system incrementally.
## Constraints
- Never break existing functionality. Parallel run with comparison. Incremental migration.
## Success Criteria
- New system handles migrated features. Parity verified. Old system decommissioning progresses.
```
