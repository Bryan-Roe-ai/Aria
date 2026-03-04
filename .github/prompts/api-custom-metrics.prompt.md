```prompt
---
agent: agent
description: "Implement API monitoring with custom metrics"
---
# API Custom Metrics
## Task
Implement custom API metrics collection.
## Requirements
1. Track request count, latency percentiles (p50/p95/p99). 2. Track error rates by endpoint and status code.
3. Track active connections and queue depth. 4. Export metrics in Prometheus or StatsD format.
5. Create alerting thresholds for key metrics.
## Constraints
- Metrics collection must be low overhead. Use standard metric names. Export every 10s.
## Success Criteria
- All key metrics tracked. Latency percentiles accurate. Alerts configured.
```
