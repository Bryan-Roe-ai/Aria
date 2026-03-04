```prompt
---
agent: agent
description: "Write unit tests following arrange-act-assert pattern"
---
# Unit Test AAA
## Task
Write unit tests following the Arrange-Act-Assert pattern.
## Requirements
1. Arrange: Set up test data, mocks, and preconditions.
2. Act: Execute the single function/method under test.
3. Assert: Verify the expected outcome with specific assertions.
4. One logical assertion per test.
5. Use descriptive test names: `test_<function>_<scenario>_<expected>`.
## Constraints
- Tests must be independent and isolated.
- No shared mutable state between tests.
- Keep arrange minimal; use fixtures for common setup.
## Success Criteria
- Each test exercises one behavior.
- Tests are readable and self-documenting.
- All assertions are specific and meaningful.
```
