```prompt
---
agent: agent
description: "Fix flaky tests that intermittently pass or fail"
---
# Fix Flaky Tests
## Task
Diagnose and fix flaky tests.
## Requirements
1. Identify flaky tests with `pytest-repeat` or CI history.
2. Categorize root cause (timing, ordering, shared state, network).
3. Fix the root cause, not just retry.
4. Add proper waits, mocks, or isolation.
5. Verify fix with repeated runs.
## Constraints
- Don't add retries as the fix; fix the underlying issue.
- Use deterministic mocks instead of real timing.
- Isolate tests from external dependencies.
## Success Criteria
- Previously flaky tests pass consistently.
- Root cause documented for future prevention.
- No new flaky patterns introduced.
```
