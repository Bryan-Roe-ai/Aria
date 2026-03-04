```prompt
---
agent: agent
description: "Test timeout and retry behavior in network operations"
---
# Timeout and Retry Tests
## Task
Write tests for timeout and retry logic in network operations.
## Requirements
1. Test connection timeout triggers after configured duration.
2. Test read timeout vs connection timeout.
3. Test retry count and backoff intervals.
4. Test retry with exponential backoff and jitter.
5. Test final failure after max retries.
## Constraints
- Use mocked delays, not real timeouts. Verify retry count precisely.
## Success Criteria
- Timeouts fire at configured intervals. Retries respect backoff. Final failure reported.
```
