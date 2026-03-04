```prompt
---
agent: agent
description: "Create pytest fixtures for reusable test setup and teardown"
---
# Pytest Fixtures
## Task
Create pytest fixtures for reusable test setup and teardown.
## Requirements
1. Define fixtures with appropriate scope (function, class, module, session).
2. Use `yield` for setup/teardown in a single fixture.
3. Parametrize fixtures for multiple configurations.
4. Use `conftest.py` for shared fixtures.
5. Add type hints to fixture return values.
## Constraints
- Use function scope by default; session only for expensive resources.
- Don't create circular fixture dependencies.
- Keep fixtures focused and composable.
## Success Criteria
- Common setup is shared through fixtures.
- Cleanup runs even on test failure.
- Fixtures are documented and discoverable.
```
