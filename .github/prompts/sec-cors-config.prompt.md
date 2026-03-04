```prompt
---
agent: agent
description: "Implement CORS security configuration"
---
# CORS Security
## Task
Configure CORS with security-first approach.
## Requirements
1. Whitelist specific origins only. 2. Restrict allowed methods per endpoint.
3. Restrict allowed headers to necessary ones. 4. Never use wildcard with credentials.
5. Validate Origin header server-side.
## Constraints
- No `Access-Control-Allow-Origin: *` with credentials. Log CORS violations.
## Success Criteria
- Only whitelisted origins allowed. Methods restricted. No wildcard with credentials.
```
