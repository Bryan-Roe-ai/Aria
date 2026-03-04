```prompt
---
agent: agent
description: "Implement secure cookie configuration"
---
# Secure Cookies
## Task
Configure cookies with security best practices.
## Requirements
1. Set Secure flag (HTTPS only). 2. Set HttpOnly flag (no JavaScript access).
3. Set SameSite=Strict or Lax. 4. Set appropriate Path and Domain.
5. Set expiration for session cookies.
## Constraints
- All auth cookies: Secure+HttpOnly+SameSite. Avoid cookie-based storage for large data.
## Success Criteria
- All cookies have security flags. SameSite set. No sensitive data in cookies without encryption.
```
