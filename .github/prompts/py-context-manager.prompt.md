```prompt
---
agent: agent
description: "Implement context managers for resource lifecycle management"
---
# Context Manager

## Task
Implement context managers for safe resource acquisition and release.

## Requirements
1. Use `__enter__`/`__exit__` or `@contextmanager` decorator.
2. Ensure cleanup runs even on exceptions.
3. Handle nested context managers with `ExitStack`.
4. Support async context managers (`__aenter__`/`__aexit__`) if needed.
5. Log resource lifecycle events for debugging.

## Constraints
- Always release resources in `__exit__`, even on exception.
- Don't suppress exceptions unless explicitly intended.
- Keep context manager scope as narrow as possible.

## Success Criteria
- Resources are always cleaned up, even on failure.
- Context manager works with `with` and `async with` statements.
- No resource leaks under any execution path.
```
