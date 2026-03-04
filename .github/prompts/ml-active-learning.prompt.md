```prompt
---
agent: agent
description: "Implement active learning for efficient data labeling"
---
# Active Learning
## Task
Implement active learning for efficient data labeling.
## Requirements
1. Select most informative samples for labeling. 2. Use uncertainty sampling or query-by-committee.
3. Iterate: label, train, select, repeat. 4. Track labeling budget vs model improvement.
5. Stop when marginal improvement diminishes.
## Constraints
- Budget labeling effort. Batch selection for efficiency. Track cost per improvement.
## Success Criteria
- Fewer labels needed for target accuracy. Budget tracked. Diminishing returns detected.
```
