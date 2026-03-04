```prompt
---
agent: agent
description: "Implement temporal tables for historical data tracking"
---
# Temporal Tables
## Task
Implement temporal (system-versioned) tables for history.
## Requirements
1. Track valid time range for each row. 2. Automatically maintain history on changes.
3. Query data at any point in time (AS OF). 4. Implement retention policy for history.
5. Index temporal queries.
## Constraints
- System-managed period columns. History table auto-populated. Query with AS OF syntax.
## Success Criteria
- Historical data tracked automatically. Point-in-time queries work. Retention enforced.
```
