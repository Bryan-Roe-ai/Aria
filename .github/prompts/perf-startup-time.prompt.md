```prompt
---
agent: agent
description: Minimize startup latency and time-to-ready for services.
---
Task:
Break down startup path and remove avoidable initialization overhead.
Requirements:
Measure cold start timeline, import/init cost, blocking dependencies, and readiness gates.
Constraints:
Do not skip critical health checks, migrations, or security initialization.
Success Criteria:
Report faster startup milestones and a validated time-to-ready improvement.
```
