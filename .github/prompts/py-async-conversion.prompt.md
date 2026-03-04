```prompt
---
agent: agent
description: "Convert synchronous code to async/await with proper concurrency patterns"
---
# Async Conversion

## Task
Convert synchronous blocking code to use async/await with proper concurrency.

## Requirements
1. Identify blocking I/O calls (network, file, database).
2. Convert to async equivalents (aiohttp, aiofiles, asyncpg, etc.).
3. Use `asyncio.gather()` for independent concurrent operations.
4. Add proper cancellation and timeout handling.
5. Ensure thread-safety for any shared mutable state.

## Constraints
- Don't mix sync and async in the same call chain without `run_in_executor`.
- Set timeouts on all network calls.
- Use semaphores to limit concurrent connections.

## Success Criteria
- All blocking I/O converted to async.
- Concurrent operations use `gather()` where independent.
- Timeouts and cancellation handled gracefully.
```
