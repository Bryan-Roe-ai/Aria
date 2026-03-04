```prompt
---
agent: agent
description: "Implement CSRF protection with token validation"
---
# CSRF Protection
## Task
Implement CSRF protection for state-changing endpoints.
## Requirements
1. Generate CSRF tokens per session. 2. Validate token on all POST/PUT/PATCH/DELETE.
3. Use double-submit cookie pattern or synchronizer token. 4. Reject requests with missing or invalid tokens.
5. Exempt API key-authenticated requests.
## Constraints
- Check Origin/Referer headers as defense-in-depth. Use SameSite cookies. Never use GET for mutations.
## Success Criteria
- CSRF tokens validated on mutations. Missing tokens rejected. SameSite cookies set.
```
