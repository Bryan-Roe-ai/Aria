```prompt
---
agent: agent
description: "Implement the factory pattern for flexible object creation"
---
# Factory Pattern

## Task
Implement a factory pattern for decoupled object creation.

## Requirements
1. Define a factory function or class that creates objects by type key.
2. Register concrete types with the factory.
3. Support configuration-driven object creation.
4. Add type hints for factory methods.
5. Handle unknown type keys with clear error messages.

## Constraints
- Keep factory logic separate from business logic.
- Use a registry dict rather than if/elif chains.
- Support lazy registration for extensibility.

## Success Criteria
- Object creation is decoupled from usage.
- New types can be added without modifying factory core.
- Unknown types produce actionable error messages.
```
