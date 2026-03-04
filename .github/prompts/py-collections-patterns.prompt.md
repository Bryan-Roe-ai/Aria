```prompt
---
agent: agent
description: "Use collections module for specialized data structures"
---
# Collections Patterns

## Task
Apply collections module data structures for cleaner, more efficient code.

## Requirements
1. Use `defaultdict` to eliminate key-existence checks.
2. Use `Counter` for counting and frequency analysis.
3. Use `deque` for O(1) append/pop from both ends.
4. Use `OrderedDict` for insertion-ordered mappings with move_to_end.
5. Use `namedtuple` or `NamedTuple` for lightweight immutable records.

## Constraints
- Prefer `collections.abc` for abstract base classes.
- Use `deque(maxlen=N)` for bounded buffers.
- Prefer `typing.NamedTuple` over `collections.namedtuple` for type hints.

## Success Criteria
- Appropriate data structure chosen for each use case.
- Code is simpler and more performant.
- No manual reimplementation of standard collection patterns.
```
