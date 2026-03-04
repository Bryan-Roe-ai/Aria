```prompt
---
agent: agent
description: "Implement CSP and security headers for web applications"
---
# Content Security Policy
## Task
Implement Content Security Policy and security headers.
## Requirements
1. Define CSP with restrictive defaults (`default-src 'self'`). 2. Allow specific external sources explicitly.
3. Enable CSP reporting for violations. 4. Set strict-transport-security header.
5. Disable inline scripts and eval.
## Constraints
- Start with report-only mode. No `unsafe-inline` or `unsafe-eval`. Use nonces for inline scripts.
## Success Criteria
- CSP blocks unauthorized resources. Violations reported. No inline scripts allowed.
```
