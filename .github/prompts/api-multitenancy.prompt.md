```prompt
---
agent: agent
description: "Implement API multitenancy with tenant isolation"
---
# API Multitenancy
## Task
Implement multitenancy with data isolation per tenant.
## Requirements
1. Identify tenant from API key, subdomain, or header.
2. Apply tenant filter to all database queries.
3. Isolate tenant data (schema-per-tenant or row-level).
4. Support tenant-specific configuration.
5. Prevent cross-tenant data access.
## Constraints
- Default deny: queries without tenant filter must fail. Test isolation rigorously.
## Success Criteria
- Tenant identified on every request. Data isolated. Cross-tenant access impossible.
```
