```prompt
---
agent: agent
description: "Implement database change data capture (CDC)"
---
# Change Data Capture
## Task
Implement CDC for real-time data change streaming.
## Requirements
1. Capture INSERT/UPDATE/DELETE events from database. 2. Stream changes to message broker.
3. Preserve change ordering. 4. Handle schema evolution.
5. Monitor CDC lag.
## Constraints
- Use database-native CDC. Preserve ordering. Handle schema changes gracefully.
## Success Criteria
- Changes captured in real-time. Ordering preserved. Schema evolution handled. Lag monitored.
```
