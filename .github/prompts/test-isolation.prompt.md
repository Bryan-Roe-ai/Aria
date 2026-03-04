```prompt
---
agent: agent
description: "Implement test isolation to prevent test pollution"
---
# Test Isolation
## Task
Ensure tests are isolated from each other.
## Requirements
1. Reset global state between tests.
2. Use fresh database transactions with rollback.
3. Clear caches and memoized values.
4. Isolate environment variables with `monkeypatch`.
5. Ensure test order doesn't matter.
## Constraints
- Run `pytest --randomly` to detect order dependencies.
- Don't use class-level setup for state that should be per-test.
- Database fixtures should use transactions, not DELETE.
## Success Criteria
- Tests pass in any order.
- No shared mutable state between tests.
- `pytest --randomly` passes consistently.
```
