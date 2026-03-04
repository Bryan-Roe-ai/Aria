```prompt
---
agent: agent
description: "Implement database multi-tenancy patterns"
---
# Database Multi-Tenancy
## Task
Implement database multi-tenancy with data isolation.
## Requirements
1. Choose strategy (schema-per-tenant, row-level, database-per-tenant). 2. Enforce tenant isolation at query level.
3. Support tenant-specific schema extensions. 4. Handle cross-tenant reporting.
5. Monitor per-tenant resource usage.
## Constraints
- Default deny: no query without tenant filter. Row-level security for row-level. Monitor usage.
## Success Criteria
- Tenant data isolated. No cross-tenant access. Per-tenant monitoring. Strategy documented.
```
