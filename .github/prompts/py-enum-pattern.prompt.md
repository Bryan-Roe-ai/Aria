```prompt
---
agent: agent
description: "Implement the enum pattern for type-safe constants and state machines"
---
# Enum Pattern

## Task
Convert string/integer constants to type-safe enums.

## Requirements
1. Define `Enum` or `StrEnum`/`IntEnum` for related constants.
2. Use `auto()` for auto-generated values where order doesn't matter.
3. Add helper methods on the enum for common operations.
4. Update all usage sites to use enum members instead of raw strings/ints.
5. Add JSON serialization support if needed.

## Constraints
- Use `StrEnum` for string-based enums that need JSON compatibility.
- Don't use `Enum` for values that genuinely need to be open-ended.
- Keep enum members UPPER_SNAKE_CASE.

## Success Criteria
- All magic strings/numbers replaced with enum members.
- Pattern matching and comparison use enum types.
- JSON serialization works correctly.
```
