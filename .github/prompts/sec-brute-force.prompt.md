```prompt
---
agent: agent
description: "Implement rate limiting for brute force protection"
---
# Brute Force Protection
## Task
Implement rate limiting specifically for brute force prevention.
## Requirements
1. Limit login attempts per account (5/15min). 2. Limit by IP for distributed attacks.
3. Implement progressive delays after failures. 4. Lock account after threshold with unlock flow.
5. Alert on suspected brute force activity.
## Constraints
- Don't reveal if account exists. Progressive delay caps at 30s. Send alert after 10 failures.
## Success Criteria
- Brute force blocked. Account locked safely. Alerts triggered. No account enumeration.
```
