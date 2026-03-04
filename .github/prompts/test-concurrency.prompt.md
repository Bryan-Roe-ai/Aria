```prompt
---
agent: agent
description: "Test concurrent code for thread safety and race conditions"
---
# Concurrency Tests
## Task
Write tests for concurrent code to detect race conditions.
## Requirements
1. Use `threading` or `asyncio` to simulate concurrent access.
2. Test shared state under concurrent modification.
3. Test lock acquisition and deadlock scenarios.
4. Use thread-safe data structures.
5. Run concurrent tests multiple times for higher confidence.
## Constraints
- Concurrency bugs are non-deterministic; run tests many iterations. Set timeouts.
## Success Criteria
- No race conditions detected. Locks work correctly. Tests stable across runs.
```
