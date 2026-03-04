```prompt
---
agent: agent
description: "Implement generator and iterator patterns for memory-efficient data processing"
---
# Generator Pattern

## Task
Implement generators for memory-efficient lazy data processing.

## Requirements
1. Convert list-building loops to generator functions with `yield`.
2. Use generator expressions where inline generation is sufficient.
3. Implement `__iter__`/`__next__` for custom iterables.
4. Chain generators with `yield from` for composed pipelines.
5. Add `send()` and `throw()` support for coroutine-style generators.

## Constraints
- Generators are single-use; document this for consumers.
- Don't materialize large datasets; keep them lazy.
- Handle `StopIteration` properly in manual iteration.

## Success Criteria
- Memory usage is constant regardless of input size.
- Generator pipeline processes data lazily end-to-end.
- No unnecessary list materializations.
```
