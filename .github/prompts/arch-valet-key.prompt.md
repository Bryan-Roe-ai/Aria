```prompt
---
agent: agent
description: "Implement valet key pattern for direct resource access"
---
# Valet Key Pattern
## Task
Implement valet key for direct client-to-resource access.
## Requirements
1. Generate time-limited access tokens. 2. Scope tokens to specific resources/operations.
3. Client accesses resource directly with token. 4. Token expires automatically.
5. Revoke tokens when needed.
## Constraints
- Minimum permissions on token. Short TTL (minutes). Scoped to specific resource.
## Success Criteria
- Clients access resources directly. Tokens scoped and time-limited. Revocation works.
```
