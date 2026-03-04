```prompt
---
agent: agent
description: "Implement API connection pooling for database efficiency"
---
# API Connection Pooling
## Task
Configure database connection pooling for API efficiency.
## Requirements
1. Set pool size based on expected concurrency. 2. Configure connection timeout and idle timeout.
3. Implement connection validation on checkout. 4. Handle connection exhaustion gracefully.
5. Monitor pool usage metrics.
## Constraints
- Pool size = CPU cores * 2 + disk spindles. Idle timeout 5 min. Validate on borrow.
## Success Criteria
- Connections pooled efficiently. Exhaustion handled. Pool metrics visible.
```
