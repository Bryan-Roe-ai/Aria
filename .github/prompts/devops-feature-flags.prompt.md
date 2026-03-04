```prompt
---
agent: agent
description: "Implement feature flag system for controlled rollouts"
---
# Feature Flags
## Task
Implement feature flag system for safe feature rollouts.
## Requirements
1. Define flags with default values. 2. Support gradual rollout (% of users).
3. Support targeting by user/group attributes. 4. Runtime toggling without deploys.
5. Audit flag changes and clean up stale flags.
## Constraints
- Default off for new features. Clean up after full rollout. Audit all changes.
## Success Criteria
- Flags toggle features without deploy. Gradual rollout works. Stale flags cleaned.
```
