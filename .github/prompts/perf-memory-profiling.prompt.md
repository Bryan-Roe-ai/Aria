```prompt
---
agent: agent
description: Analyze allocation pressure, leaks, and memory growth risks.
---
Task:
Measure memory behavior across steady-state and peak workloads to find leaks and churn.
Requirements:
Collect RSS/heap trends, allocation hotspots, object lifetimes, and top retaining paths.
Constraints:
Do not disable safeguards; preserve correctness and avoid unbounded caching.
Success Criteria:
Provide baseline vs improved memory profile, leak status, and prioritized remediation steps.
```
