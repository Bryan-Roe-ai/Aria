```prompt
---
agent: agent
description: "Implement clean architecture with dependency rule"
---
# Clean Architecture
## Task
Structure code using clean architecture principles.
## Requirements
1. Entities (core business rules). 2. Use cases (application business rules).
3. Interface adapters (controllers, presenters). 4. Frameworks (DB, web, external).
5. Dependencies always point inward.
## Constraints
- Inner layers never depend on outer. Use interfaces at boundaries. DI for wiring.
## Success Criteria
- Layers clearly separated. Dependency rule enforced. Business logic framework-free.
```
