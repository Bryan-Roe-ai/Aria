```prompt
---
agent: agent
description: "Implement threading for I/O-bound concurrent operations"
---
# Threading Patterns

## Task
Implement threading for concurrent I/O-bound operations.

## Requirements
1. Use `ThreadPoolExecutor` for managed thread pools.
2. Protect shared state with `threading.Lock` or `RLock`.
3. Use `threading.Event` for signaling between threads.
4. Implement thread-safe queues with `queue.Queue`.
5. Set daemon flags and timeouts appropriately.

## Constraints
- Python GIL limits threading for CPU-bound work; use for I/O only.
- Always use context managers (`with lock:`) for locks.
- Set `daemon=True` for background threads that should not block exit.

## Success Criteria
- I/O operations run concurrently with proper synchronization.
- No race conditions or deadlocks.
- Thread pool cleans up on shutdown.
```
