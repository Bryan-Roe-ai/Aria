```prompt
---
agent: agent
description: Increase sustained throughput without violating SLOs.
---
Task:
Tune concurrency, batching, and resource usage to raise stable throughput.
Requirements:
Measure QPS/RPS under load, saturation points, error rates, and tail latency impact.
Constraints:
No tuning that trades reliability for raw volume; keep SLO and error budgets respected.
Success Criteria:
Show reproducible throughput gains with bounded latency and error behavior.
```
