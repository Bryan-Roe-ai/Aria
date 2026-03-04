```prompt
---
agent: agent
description: "Implement API feature flags for controlled rollout"
---
# API Feature Flags
## Task
Implement feature flags for controlled API feature rollout.
## Requirements
1. Define flags in config with default state. 2. Support percentage-based rollout.
3. Support user/group targeting. 4. Evaluate flags per-request with minimal latency.
5. Support runtime flag changes without restart.
## Constraints
- Flags must be fast to evaluate (< 1ms). Cache flag state. Log flag evaluations.
## Success Criteria
- Features toggled without deploy. Percentage rollout works. Targeting accurate.
```
