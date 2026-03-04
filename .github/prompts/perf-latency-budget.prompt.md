```prompt
---
agent: agent
description: Build and enforce a latency budget across request stages.
---
Task:
Define a latency budget per stage and locate budget overruns in the critical path.
Requirements:
Map request timeline, stage percentiles, queueing delay, and external dependency latency.
Constraints:
Use p95/p99 targets, not averages alone, and avoid hidden async backlog growth.
Success Criteria:
Produce an agreed budget table, overrun root causes, and actionable mitigations.
```
