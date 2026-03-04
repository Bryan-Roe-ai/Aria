```prompt
---
agent: agent
description: "Implement secure database access patterns"
---
# Secure Database Access
## Task
Implement secure database access patterns.
## Requirements
1. Use parameterized queries only. 2. Apply least-privilege database users per service.
3. Encrypt connections with TLS. 4. Rotate database credentials regularly.
5. Audit all data access queries.
## Constraints
- Never concatenate SQL strings. Separate read/write DB users. Connection pooling with TLS.
## Success Criteria
- All queries parameterized. Least-privilege users. Connections encrypted. Access audited.
```
