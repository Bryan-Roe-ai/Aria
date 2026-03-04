```prompt
---
agent: agent
description: "Write boundary value tests for edge case coverage"
---
# Boundary Tests
## Task
Write boundary value tests for edge case coverage.
## Requirements
1. Test at exact boundaries (0, 1, max, max+1).
2. Test empty collections, None values, empty strings.
3. Test numeric limits (overflow, underflow, precision).
4. Test time boundaries (midnight, DST transitions, leap years).
5. Test string boundaries (empty, max length, unicode, special chars).
## Constraints
- Each boundary test should isolate one boundary.
- Document why each boundary matters.
- Include both valid and invalid boundary values.
## Success Criteria
- All boundaries for the target function are covered.
- Edge cases don't crash or produce incorrect results.
- Boundary behavior is documented.
```
