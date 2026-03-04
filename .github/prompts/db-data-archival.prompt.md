```prompt
---
agent: agent
description: "Implement database data archival strategy"
---
# Data Archival
## Task
Implement data archival for historical data management.
## Requirements
1. Define archival criteria (age, status). 2. Move archived data to cold storage.
3. Maintain query access to archived data. 4. Implement unarchival process.
5. Monitor archival pipeline.
## Constraints
- Archival must not impact live queries. Archive > 90 days old. Queryable from archive.
## Success Criteria
- Old data archived automatically. Live performance improved. Archived data accessible.
```
