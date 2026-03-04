```prompt
---
agent: agent
description: "Write regression tests for previously reported bugs"
---
# Regression Tests
## Task
Write regression tests for fixed bugs to prevent recurrence.
## Requirements
1. Reproduce the bug scenario in a test.
2. Verify the fix resolves the issue.
3. Add test before applying the fix (TDD approach).
4. Include bug ID in test docstring.
5. Cover the specific input that triggered the bug.
## Constraints
- Regression test must fail without the fix. Keep focused on the specific bug.
## Success Criteria
- Bug cannot recur without failing the regression test. Bug ID documented.
```
