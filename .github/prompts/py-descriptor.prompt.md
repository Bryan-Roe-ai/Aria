```prompt
---
agent: agent
description: "Implement descriptors for reusable attribute behavior"
---
# Descriptor Pattern

## Task
Implement descriptors for reusable attribute access control.

## Requirements
1. Define descriptors with `__get__`, `__set__`, `__delete__`.
2. Use descriptors for validation, computed properties, or lazy loading.
3. Store per-instance data correctly (avoid class-level sharing).
4. Add type hints for descriptor return types.
5. Document descriptor behavior for consumers.

## Constraints
- Store instance data in `instance.__dict__`, not on the descriptor.
- Use `__set_name__` for automatic attribute name discovery.
- Keep descriptor logic focused on a single concern.

## Success Criteria
- Attribute access is controlled with reusable descriptor logic.
- Per-instance data is isolated correctly.
- Descriptor behavior is well-documented.
```
