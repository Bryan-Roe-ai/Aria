```prompt
---
agent: agent
description: "Add parametrized tests for data-driven testing with multiple inputs"
---
# Parametrized Tests
## Task
Add parametrized tests for data-driven testing.
## Requirements
1. Use `@pytest.mark.parametrize` with named test cases.
2. Include edge cases: empty, None, boundary values, large inputs.
3. Use `pytest.param` with `id` for readable test names.
4. Group related parameters logically.
5. Add `marks=pytest.mark.xfail` for known failures.
## Constraints
- Each parameter set must be independent.
- Don't parametrize to avoid writing real tests.
- Keep parameter sets readable; use constants for complex data.
## Success Criteria
- Multiple input scenarios covered efficiently.
- Edge cases and boundary values included.
- Test names clearly indicate the scenario.
```
