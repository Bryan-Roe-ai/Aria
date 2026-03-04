```prompt
---
agent: agent
description: "Implement vertical slice architecture"
---
# Vertical Slice Architecture
## Task
Structure code using vertical slice architecture.
## Requirements
1. Organize by feature, not by technical layer. 2. Each slice contains handler, validation, data access.
3. Minimize coupling between slices. 4. Share only truly common infrastructure.
5. Test each slice independently.
## Constraints
- Features in separate folders. Shared code is infrastructure only. Each slice self-contained.
## Success Criteria
- Features organized by slice. Independent testing. Minimal cross-slice coupling.
```
