```prompt
---
agent: agent
description: "Test cleanup and teardown procedures for resource management"
---
# Cleanup Tests
## Task
Write tests to verify cleanup and teardown procedures.
## Requirements
1. Verify all resources are released after operations.
2. Test cleanup runs even on exceptions.
3. Test cleanup ordering (LIFO).
4. Test partial cleanup on partial failures.
5. Test idempotent cleanup (safe to call multiple times).
## Constraints
- Resource leaks are critical bugs. Test cleanup under error conditions.
## Success Criteria
- All resources released. Cleanup survives errors. No resource leaks.
```
