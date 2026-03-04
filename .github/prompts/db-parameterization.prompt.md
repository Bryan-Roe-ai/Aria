```prompt
---
agent: agent
description: "Implement database query parameterization and prepared statements"
---
# Query Parameterization
## Task
Implement parameterized queries to prevent SQL injection.
## Requirements
1. Use parameterized queries for all user input. 2. Never concatenate SQL strings.
3. Use ORM query builders. 4. Validate inputs before query.
5. Test with SQL injection payloads.
## Constraints
- Zero tolerance for string concatenation in SQL. Use ORM or parameterized only.
## Success Criteria
- All queries parameterized. No string concatenation. Injection tests pass.
```
