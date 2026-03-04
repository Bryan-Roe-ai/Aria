```prompt
---
agent: agent
description: "Implement input validation against OWASP Top 10 vulnerabilities"
---
# OWASP Input Validation
## Task
Implement input validation against OWASP Top 10 attack vectors.
## Requirements
1. Validate all user inputs (form, query, header, cookie). 2. Prevent SQL injection with parameterized queries.
3. Prevent XSS with output encoding. 4. Prevent CSRF with tokens.
5. Prevent path traversal with canonicalization.
## Constraints
- Input validation is defense-in-depth; complement with output encoding. Use allowlists over denylists.
## Success Criteria
- OWASP Top 10 mitigated. All inputs validated. No injection vectors.
```
