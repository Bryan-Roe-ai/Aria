```instructions
---
name: "Tests-Python"
description: "Testing standards for Python tests"
applyTo: "tests/**/*.py"
---
# Test Authoring Guidance

- Prefer focused unit tests with explicit Arrange/Act/Assert structure.
- Add regression tests for every bug fix.
- Mock external network/cloud dependencies unless explicitly testing integration.
- Keep test fixtures deterministic and lightweight.
- Name tests for behavior, not implementation details.
- For orchestration/quantum flows, include dry-run and error-path coverage.
```
