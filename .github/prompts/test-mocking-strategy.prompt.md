```prompt
---
agent: agent
description: "Implement mocking and patching for isolated unit tests"
---
# Mocking Strategy
## Task
Implement mocking and patching for isolated unit tests.
## Requirements
1. Use `unittest.mock.patch` to replace external dependencies.
2. Use `MagicMock` for objects and `AsyncMock` for async functions.
3. Configure mock return values and side effects.
4. Assert mock calls: call count, arguments, order.
5. Patch at the import location, not the definition.
## Constraints
- Patch where things are used, not where defined.
- Don't over-mock; test real logic, mock only boundaries.
- Reset mocks between tests.
## Success Criteria
- External dependencies are isolated in unit tests.
- Mock assertions verify interaction contracts.
- Tests don't depend on external service availability.
```
