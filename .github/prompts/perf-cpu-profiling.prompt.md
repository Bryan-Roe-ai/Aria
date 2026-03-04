```prompt
---
agent: agent
description: Profile CPU hot paths and prioritize high-ROI fixes.
---
Task:
Profile CPU usage for representative scenarios and isolate dominant hot paths.
Requirements:
Capture wall/CPU time, flamegraph (or equivalent), and top 5 functions by self and total cost.
Constraints:
Avoid behavior changes, keep instrumentation lightweight, and note measurement variance.
Success Criteria:
Report baseline vs optimized metrics, expected impact per fix, and a ranked execution plan.
```
