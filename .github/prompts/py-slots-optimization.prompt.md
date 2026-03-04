```prompt
---
agent: agent
description: "Optimize memory with __slots__ for high-volume object classes"
---
# Slots Optimization

## Task
Add `__slots__` to classes for memory optimization.

## Requirements
1. Identify classes with many instances (data objects, nodes, records).
2. Add `__slots__` with all attribute names.
3. Handle inheritance with slots correctly.
4. Measure memory savings before and after.
5. Update any code relying on `__dict__` access.

## Constraints
- `__slots__` prevents dynamic attribute addition; document this.
- Include `__weakref__` in slots if weak references are needed.
- Handle multiple inheritance with slots carefully.

## Success Criteria
- Memory per instance is reduced significantly.
- No runtime errors from missing dynamic attributes.
- Memory savings measured and documented.
```
