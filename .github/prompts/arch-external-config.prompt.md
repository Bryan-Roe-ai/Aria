```prompt
---
agent: agent
description: "Implement external configuration store pattern"
---
# External Configuration Store
## Task
Implement external configuration store for centralized config.
## Requirements
1. Store config in external service (Azure App Config, Consul). 2. Support dynamic config updates without restart.
3. Version configuration changes. 4. Support feature flags alongside config.
5. Audit config modifications.
## Constraints
- Config changes audited. Support rollback. Cache locally with refresh interval.
## Success Criteria
- Config centralized. Dynamic updates work. Changes audited and rollbackable.
```
