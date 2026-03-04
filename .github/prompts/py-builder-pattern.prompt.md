```prompt
---
agent: agent
description: "Implement the builder pattern for complex object construction"
---
# Builder Pattern

## Task
Implement the builder pattern for step-by-step object construction.

## Requirements
1. Create a builder class with fluent method chaining.
2. Validate required fields in the `build()` method.
3. Support optional fields with sensible defaults.
4. Add type hints for all builder methods.
5. Make the built object immutable after construction.

## Constraints
- Validate all constraints in `build()`, not in individual setters.
- Return `self` from setter methods for chaining.
- Keep builder separate from the built class.

## Success Criteria
- Complex objects are built step-by-step with validation.
- Missing required fields produce clear error messages.
- Built objects are immutable.
```
