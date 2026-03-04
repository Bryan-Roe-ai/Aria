```prompt
---
agent: agent
description: "Implement API CORS configuration for cross-origin access"
---
# API CORS Configuration
## Task
Configure CORS for API cross-origin access.
## Requirements
1. Set `Access-Control-Allow-Origin` with specific origins.
2. Configure allowed methods and headers.
3. Handle preflight OPTIONS requests.
4. Set `Access-Control-Max-Age` for preflight caching.
5. Support credentials with `Access-Control-Allow-Credentials`.
## Constraints
- Never use wildcard `*` with credentials. Whitelist specific origins only.
## Success Criteria
- CORS headers set correctly. Preflight handled. Cross-origin requests work from allowed origins.
```
