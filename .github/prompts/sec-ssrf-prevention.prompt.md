```prompt
---
agent: agent
description: "Implement SSRF (Server-Side Request Forgery) prevention"
---
# SSRF Prevention
## Task
Prevent server-side request forgery attacks.
## Requirements
1. Validate and sanitize all URLs from user input. 2. Block requests to internal/private IP ranges.
3. Use allowlist for permitted external domains. 4. Disable redirects or validate redirect targets.
5. Use network-level controls as defense-in-depth.
## Constraints
- Block RFC 1918, link-local, loopback addresses. No DNS rebinding. Validate after DNS resolution.
## Success Criteria
- Internal networks inaccessible via SSRF. URLs validated. Redirects controlled.
```
