```prompt
---
agent: agent
description: "Implement API authentication with JWT tokens"
---
# API JWT Authentication
## Task
Implement JWT-based authentication for API endpoints.
## Requirements
1. Generate JWT tokens on login with appropriate claims.
2. Validate tokens on each request with middleware.
3. Handle token expiration and refresh.
4. Use asymmetric keys for signing (RS256).
5. Include user ID, roles, and expiry in claims.
## Constraints
- Never store JWTs in localStorage. Set short expiry (15 min). Use secure refresh flow.
## Success Criteria
- Tokens generated and validated correctly. Expiry enforced. Refresh flow works.
```
