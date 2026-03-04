```prompt
---
agent: agent
description: "Implement the singleton pattern correctly in Python"
---
# Singleton Pattern

## Task
Implement a thread-safe singleton pattern.

## Requirements
1. Use module-level instance or `__new__` override.
2. Ensure thread safety with locks if needed.
3. Support lazy initialization.
4. Make singleton testable (allow reset for tests).
5. Document that the class is a singleton.

## Constraints
- Prefer module-level singleton over class-based where simple.
- Don't use metaclass singletons unless necessary.
- Ensure `__init__` doesn't re-run on repeated access.

## Success Criteria
- Only one instance exists across the application.
- Thread-safe initialization.
- Tests can reset the singleton for isolation.
```
