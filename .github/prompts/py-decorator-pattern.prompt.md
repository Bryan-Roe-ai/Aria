```prompt
---
agent: agent
description: "Implement the decorator pattern for cross-cutting concerns"
---
# Decorator Pattern

## Task
Implement decorators for cross-cutting concerns like caching, retry, timing, or auth.

## Requirements
1. Use `functools.wraps` to preserve function metadata.
2. Support both `@decorator` and `@decorator(args)` syntax.
3. Handle async functions transparently if needed.
4. Add proper type hints for the decorator.
5. Document decorator behavior and parameters.

## Constraints
- Decorators must be composable (stackable).
- Preserve original function signature for IDE support.
- Keep decorator logic minimal; delegate to helper functions.

## Success Criteria
- Decorator works on both sync and async functions.
- `functools.wraps` preserves `__name__`, `__doc__`, `__module__`.
- Decorator is well-documented with usage examples.
```
