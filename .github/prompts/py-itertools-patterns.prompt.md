```prompt
---
agent: agent
description: "Use itertools for efficient iteration patterns and combinatorics"
---
# Itertools Patterns

## Task
Apply itertools utilities for efficient iteration and data processing.

## Requirements
1. Use `chain` for flattening nested iterables.
2. Apply `groupby` for grouping sorted data.
3. Use `islice` for efficient sequence slicing.
4. Apply `product`, `combinations`, `permutations` for combinatorics.
5. Use `tee` for duplicating iterators.

## Constraints
- `groupby` requires pre-sorted input; sort before grouping.
- Itertools return iterators (single-use); document this.
- Prefer itertools over manual loops for clarity and performance.

## Success Criteria
- Complex iteration patterns replaced with itertools calls.
- Memory usage is constant for streaming operations.
- Code is more readable with descriptive itertools usage.
```
