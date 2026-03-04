```prompt
---
agent: agent
description: "Implement CI pipeline optimization for speed"
---
# CI Optimization
## Task
Optimize CI pipeline for faster feedback.
## Requirements
1. Parallelize independent jobs. 2. Cache dependencies and build artifacts.
3. Use incremental builds. 4. Skip unchanged components (monorepo).
5. Track pipeline metrics (duration, failure rate).
## Constraints
- Target < 10 min for PR pipeline. Cache hit > 90%. Skip tests for unchanged code.
## Success Criteria
- Pipeline time reduced. Caching effective. Parallel jobs utilized.
```
