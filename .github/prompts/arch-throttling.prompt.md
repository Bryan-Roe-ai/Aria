```prompt
---
agent: agent
description: "Implement throttling pattern for resource protection"
---
# Throttling Pattern
## Task
Implement throttling to protect resources from overload.
## Requirements
1. Define resource consumption limits. 2. Monitor current consumption.
3. Reject or queue excess requests. 4. Implement graduated throttling (warn, slow, reject).
5. Alert on sustained high throttling.
## Constraints
- Protect downstream resources. Graduated response. Alert on sustained throttle.
## Success Criteria
- Resources protected from overload. Graduated response works. Alerts trigger.
```
