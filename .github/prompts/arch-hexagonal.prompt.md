```prompt
---
agent: agent
description: "Implement hexagonal architecture (ports and adapters)"
---
# Hexagonal Architecture
## Task
Structure code using hexagonal (ports and adapters) architecture.
## Requirements
1. Define ports (interfaces) for external interactions. 2. Implement adapters for each port.
3. Keep domain logic free of framework dependencies. 4. Inject adapters via dependency injection.
5. Test domain with mock adapters.
## Constraints
- Domain has no imports from infrastructure. Adapters implement port interfaces. DI required.
## Success Criteria
- Domain is pure. Adapters are swappable. Testing with mocks easy.
```
