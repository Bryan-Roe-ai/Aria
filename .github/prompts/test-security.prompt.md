```prompt
---
agent: agent
description: "Write security tests for authentication, authorization, and input validation"
---
# Security Tests
## Task
Write security tests for auth and input validation.
## Requirements
1. Test authentication (valid/invalid/expired tokens).
2. Test authorization (role-based access control).
3. Test input validation (SQL injection, XSS, path traversal).
4. Test rate limiting and brute force protection.
5. Test CORS and security headers.
## Constraints
- Security tests should cover OWASP Top 10.
- Use dedicated security testing tools where available.
- Don't skip security tests for speed.
## Success Criteria
- Auth bypasses are detected. Injection attacks are blocked. Headers are correct.
```
