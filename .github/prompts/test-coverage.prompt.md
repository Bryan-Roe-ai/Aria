```prompt
---
agent: agent
description: "Achieve target code coverage with meaningful tests"
---
# Code Coverage
## Task
Increase code coverage with meaningful tests.
## Requirements
1. Identify uncovered code with `pytest --cov` and HTML reports.
2. Prioritize coverage for business logic over boilerplate.
3. Cover all branches (if/else, try/except, loops).
4. Test error paths, not just happy paths.
5. Add `# pragma: no cover` only for truly untestable code.
## Constraints
- Don't write meaningless tests just for coverage.
- Focus on critical paths first.
- 100% coverage is not the goal; meaningful coverage is.
## Success Criteria
- Coverage targets met for critical modules.
- All branches exercised with meaningful assertions.
- Coverage reports are actionable.
```
