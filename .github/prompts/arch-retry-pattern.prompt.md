```prompt
---
agent: agent
description: "Implement retry with exponential backoff and jitter"
---
# Retry Pattern
## Task
Implement retry logic with exponential backoff and jitter.
## Requirements
1. Define retryable vs non-retryable errors. 2. Implement exponential backoff (base * 2^attempt).
3. Add random jitter to prevent thundering herd. 4. Set max retries and max delay.
5. Log each retry attempt.
## Constraints
- Max 5 retries. Max delay 30s. Jitter ±25%. Don't retry 4xx client errors.
## Success Criteria
- Transient failures recovered. Backoff prevents overload. Jitter prevents sync.
```
