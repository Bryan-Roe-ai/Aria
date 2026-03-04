```prompt
---
agent: agent
description: "Implement geode/deployment stamp pattern for geo-distribution"
---
# Deployment Stamp
## Task
Implement deployment stamp for geo-distributed services.
## Requirements
1. Define stamp (complete deployment unit per region). 2. Route users to nearest stamp.
3. Replicate data between stamps. 4. Handle stamp-level failures.
5. Support independent stamp scaling.
## Constraints
- Each stamp is self-contained. Data replication handles conflicts. Route by geography.
## Success Criteria
- Regional stamps operational. Users routed to nearest. Failures isolated per stamp.
```
