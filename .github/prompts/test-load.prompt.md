```prompt
---
agent: agent
description: "Implement load testing for API endpoint throughput and latency"
---
# Load Testing
## Task
Implement load tests for API throughput and latency.
## Requirements
1. Define load scenarios (ramp-up, steady-state, spike).
2. Use locust, k6, or ab for load generation.
3. Measure p50, p95, p99 latencies and throughput.
4. Test scaling behavior and identify bottlenecks.
5. Document baseline metrics and thresholds.
## Constraints
- Run against test environments, never production.
- Set realistic load patterns based on expected traffic.
- Monitor resource utilization during tests.
## Success Criteria
- Latency targets met at expected load.
- Scaling behavior documented.
- Bottlenecks identified and ranked.
```
