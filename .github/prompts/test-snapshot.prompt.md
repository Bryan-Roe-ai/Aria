```prompt
---
agent: agent
description: "Implement snapshot testing for output regression detection"
---
# Snapshot Tests
## Task
Implement snapshot testing for output regression detection.
## Requirements
1. Capture output (JSON, HTML, text) as a reference snapshot.
2. Compare current output against saved snapshot.
3. Update snapshots when changes are intentional.
4. Store snapshots in version control.
5. Use readable diff format for snapshot mismatches.
## Constraints
- Normalize non-deterministic values (timestamps, UUIDs) before snapshotting.
- Review snapshot updates carefully before committing.
- Keep snapshots small and focused.
## Success Criteria
- Output regressions detected automatically.
- Snapshot updates require intentional action.
- Diffs are readable and actionable.
```
