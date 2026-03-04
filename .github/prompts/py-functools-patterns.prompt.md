```prompt
---
agent: agent
description: "Implement functools patterns: lru_cache, partial, reduce, singledispatch"
---
# Functools Patterns

## Task
Apply functools utilities for functional programming patterns.

## Requirements
1. Use `lru_cache` for memoizing pure functions with hashable arguments.
2. Apply `partial` to create specialized versions of general functions.
3. Use `singledispatch` for type-based function overloading.
4. Apply `reduce` for accumulation patterns.
5. Document cache invalidation strategy for `lru_cache`.

## Constraints
- Only cache pure functions with hashable arguments.
- Set `maxsize` on `lru_cache` to bound memory usage.
- Document `partial` usage clearly for readability.

## Success Criteria
- Pure functions are memoized with bounded caches.
- Dispatch functions handle all expected types.
- Cache hit rates are monitored where relevant.
```
