```prompt
---
agent: agent
description: "Implement API request throttling per client"
---
# API Throttling
## Task
Implement graduated API throttling per client tier.
## Requirements
1. Define tier limits (free: 100/hr, pro: 1000/hr, enterprise: 10000/hr).
2. Track usage per API key in distributed cache.
3. Return throttling headers with remaining quota.
4. Support burst allowance above sustained rate.
5. Alert when clients approach limits.
## Constraints
- Use Redis or similar for distributed tracking. Grace period before hard limit.
## Success Criteria
- Throttling enforced per tier. Usage tracked accurately. Burst allowance works.
```
