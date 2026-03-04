```prompt
---
agent: agent
description: "Implement security headers for API and web responses"
---
# Security Response Headers
## Task
Apply comprehensive security headers to all responses.
## Requirements
1. X-Content-Type-Options: nosniff. 2. X-Frame-Options: DENY.
3. X-XSS-Protection: 0 (rely on CSP). 4. Referrer-Policy: strict-origin-when-cross-origin.
5. Permissions-Policy: restrict features.
## Constraints
- Apply to all responses via middleware. Test headers in CI.
## Success Criteria
- All security headers present. Features restricted. Server info hidden.
```
