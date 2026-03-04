```prompt
---
agent: agent
description: "Implement weak references to prevent memory leaks in caches and callbacks"
---
# Weakref Pattern

## Task
Use weak references to prevent memory leaks in caches and observer patterns.

## Requirements
1. Replace strong references with `weakref.ref` for cached objects.
2. Use `WeakValueDictionary` for caches that shouldn't prevent GC.
3. Use `weakref.finalize` for cleanup callbacks.
4. Handle dead references gracefully.
5. Test that objects are garbage-collected when expected.

## Constraints
- Not all types support weak references (e.g., `int`, `str`).
- Always check if weak reference is alive before dereferencing.
- Use `WeakSet` for observer/listener collections.

## Success Criteria
- No memory leaks from lingering strong references.
- Dead references handled without errors.
- GC behavior verified in tests.
```
