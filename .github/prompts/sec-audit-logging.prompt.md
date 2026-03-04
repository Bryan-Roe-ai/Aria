```prompt
---
agent: agent
description: "Implement audit logging for security-sensitive operations"
---
# Security Audit Logging
## Task
Implement audit logging for security-sensitive operations.
## Requirements
1. Log authentication events (login, logout, failure). 2. Log authorization decisions (allowed/denied).
3. Log data access for PII/sensitive data. 4. Log configuration changes.
5. Make audit logs tamper-resistant.
## Constraints
- Audit logs immutable. Include timestamp, user, action, resource, result. Ship to SIEM.
## Success Criteria
- All security events logged. Logs tamper-resistant. Shipped to SIEM. No PII in logs.
```
