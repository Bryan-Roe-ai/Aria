```prompt
---
agent: agent
description: "Implement the strategy pattern for swappable algorithms"
---
# Strategy Pattern

## Task
Implement the strategy pattern for interchangeable algorithms.

## Requirements
1. Define a strategy Protocol/ABC with a common interface.
2. Implement concrete strategies for each algorithm variant.
3. Use dependency injection to provide the strategy at runtime.
4. Support configuration-driven strategy selection.
5. Add a default strategy for fallback behavior.

## Constraints
- Strategies must be stateless or manage their own state.
- Use Protocol-based typing rather than ABC inheritance.
- Strategy selection should be explicit, not implicit.

## Success Criteria
- Algorithms are swappable without code changes.
- Strategy selection driven by config or parameters.
- Default strategy handles unknown configurations gracefully.
```
