```prompt
---
agent: agent
description: "Implement dependency injection for testable, decoupled code"
---
# Dependency Injection

## Task
Refactor code to use dependency injection for better testability.

## Requirements
1. Identify tightly coupled dependencies (database, API clients, config).
2. Extract interfaces (Protocols) for each dependency.
3. Inject dependencies through constructor parameters.
4. Provide default implementations for production use.
5. Support override for testing with mocks/fakes.

## Constraints
- Don't over-engineer; inject only external dependencies.
- Prefer constructor injection over setter injection.
- Keep the DI container simple; avoid framework-level DI.

## Success Criteria
- Dependencies are injected, not created internally.
- Unit tests can provide mock implementations.
- Production code uses sensible defaults.
```
