```prompt
---
agent: agent
description: "Convert classes to dataclasses or Pydantic models for cleaner data structures"
---
# Dataclass Migration

## Task
Convert plain classes to dataclasses or Pydantic models for cleaner data handling.

## Requirements
1. Identify classes that are primarily data containers.
2. Convert to `@dataclass` with appropriate field types.
3. Use `field(default_factory=...)` for mutable defaults.
4. Add `frozen=True` for immutable value objects.
5. Implement `__post_init__` for validation logic.

## Constraints
- Don't convert classes with complex inheritance hierarchies blindly.
- Use Pydantic for external data validation; dataclasses for internal structs.
- Preserve existing serialization behavior.

## Success Criteria
- Data classes are cleaner with less boilerplate.
- Immutable objects use `frozen=True`.
- Validation logic preserved in `__post_init__` or Pydantic validators.
```
