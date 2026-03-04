```prompt
---
agent: agent
description: "Implement Backend-for-Frontend (BFF) pattern"
---
# Backend for Frontend
## Task
Implement BFF pattern for client-specific APIs.
## Requirements
1. Create dedicated API layer per client type (web, mobile, internal). 2. Aggregate backend calls.
3. Transform data for client-specific needs. 4. Handle client-specific auth flows.
5. Cache client-specific responses.
## Constraints
- One BFF per client type. BFF orchestrates backends. Keep BFF thin.
## Success Criteria
- Client-specific APIs optimized. Backend calls aggregated. Responses tailored per client.
```
