```prompt
---
agent: agent
description: "Implement database data deduplication"
---
# Data Deduplication
## Task
Identify and remove duplicate records from database.
## Requirements
1. Define deduplication criteria (exact match, fuzzy). 2. Identify duplicates with SQL window functions.
3. Choose master record per duplicate group. 4. Merge related records to master.
5. Archive or delete duplicates.
## Constraints
- Preserve oldest or most complete record. Update FK references. Log all merges.
## Success Criteria
- Duplicates identified and merged. References updated. Original data preserved in audit.
```
