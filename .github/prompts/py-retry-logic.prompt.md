```prompt
---
agent: agent
description: "Implement retry logic with exponential backoff and jitter"
---
# Retry Logic

## Task
Add retry logic with exponential backoff for transient failures.

## Requirements
1. Implement retry with configurable max attempts and base delay.
2. Use exponential backoff with random jitter.
3. Define which exceptions are retryable.
4. Add circuit breaker pattern for persistent failures.
5. Log each retry attempt with attempt number and delay.

## Constraints
- Only retry on transient/recoverable errors.
- Set a maximum total timeout to prevent infinite waits.
- Support both sync and async retry.

## Success Criteria
- Transient failures recover automatically.
- Backoff prevents thundering herd on service recovery.
- Circuit breaker stops retrying on persistent failures.
```
