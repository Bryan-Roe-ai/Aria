```prompt
---
agent: agent
description: "Implement API security headers for protection"
---
# API Security Headers
## Task
Configure security headers for API protection.
## Requirements
1. Set `Strict-Transport-Security` (HSTS). 2. Set `X-Content-Type-Options: nosniff`.
3. Set `X-Frame-Options: DENY`. 4. Set `Content-Security-Policy` for API responses.
5. Remove `Server` and `X-Powered-By` headers.
## Constraints
- HSTS max-age minimum 1 year. Include subdomains. Don't leak server info.
## Success Criteria
- All security headers present. Server info removed. HSTS enforced.
```
