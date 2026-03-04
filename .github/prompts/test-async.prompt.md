```prompt
---
agent: agent
description: "Write tests for async/await code with proper event loop management"
---
# Async Tests
## Task
Write tests for async code with proper event loop management.
## Requirements
1. Use `pytest-asyncio` with `@pytest.mark.asyncio`.
2. Create async fixtures with `@pytest_asyncio.fixture`.
3. Test async generators and context managers.
4. Test concurrent operations and race conditions.
5. Add timeouts for async operations.
## Constraints
- Use `asyncio_mode = "auto"` in pytest config.
- Don't create new event loops manually in tests.
- Handle `CancelledError` in test cleanup.
## Success Criteria
- Async code tested without blocking.
- Concurrent behavior verified.
- No event loop warnings or cleanup issues.
```
