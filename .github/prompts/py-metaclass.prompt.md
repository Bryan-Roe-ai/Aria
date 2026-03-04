```prompt
---
agent: agent
description: "Implement metaclasses for class creation customization"
---
# Metaclass Pattern

## Task
Implement metaclasses for advanced class creation customization.

## Requirements
1. Define a metaclass with `__new__` and/or `__init_subclass__`.
2. Use metaclass for automatic registration, validation, or transformation.
3. Prefer `__init_subclass__` over full metaclass when sufficient.
4. Document the metaclass behavior clearly.
5. Ensure compatibility with standard inheritance.

## Constraints
- Use metaclasses sparingly; prefer simpler alternatives first.
- Avoid metaclass conflicts with multiple inheritance.
- Keep metaclass logic minimal and well-documented.

## Success Criteria
- Class creation is customized as intended.
- Subclasses are automatically registered/validated.
- No conflicts with standard Python class machinery.
```
