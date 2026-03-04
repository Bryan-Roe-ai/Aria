```prompt
---
agent: agent
description: "Implement anti-corruption layer for legacy integration"
---
# Anti-Corruption Layer
## Task
Implement anti-corruption layer between new and legacy systems.
## Requirements
1. Translate legacy interfaces to domain model. 2. Isolate domain from legacy concepts.
3. Handle data format differences. 4. Map error codes between systems.
5. Monitor translation health.
## Constraints
- Legacy changes should not propagate to domain. Translation bidirectional. Monitor failures.
## Success Criteria
- Domain isolated from legacy. Translation correct. Errors mapped. Failures monitored.
```
