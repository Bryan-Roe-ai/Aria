```prompt
---
agent: agent
description: "Implement security code review checklist"
---
# Security Code Review
## Task
Apply security code review checklist to changes.
## Requirements
1. Check for hardcoded secrets. 2. Check for SQL injection vectors.
3. Check for XSS in output rendering. 4. Check for missing auth/authz checks.
5. Check for insecure cryptographic usage.
## Constraints
- Review all external-facing code changes. Use automated scanners as supplement.
## Success Criteria
- No secrets in code. No injection vectors. Auth checked. Crypto reviewed.
```
