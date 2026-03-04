```prompt
---
agent: agent
description: "Implement property pattern for controlled attribute access"
---
# Property Pattern

## Task
Use `@property` for computed attributes, validation, and encapsulation.

## Requirements
1. Define getters with `@property` for computed values.
2. Add setters with `@<name>.setter` for validated assignment.
3. Add deleters with `@<name>.deleter` for cleanup.
4. Cache expensive computed properties with `@functools.cached_property`.
5. Document property behavior in docstrings.

## Constraints
- Properties should be lightweight; avoid heavy computation in getters.
- Use `cached_property` for expensive one-time computations.
- Don't use properties for side effects; keep them predictable.

## Success Criteria
- Attributes are validated on assignment.
- Computed properties are efficient and cached appropriately.
- Encapsulation is maintained without exposing internals.
```
