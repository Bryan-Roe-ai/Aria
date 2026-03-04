```prompt
---
agent: agent
description: "Implement distributed tracing across microservices"
---
# Distributed Tracing
## Task
Implement distributed tracing across services.
## Requirements
1. Instrument services with OpenTelemetry. 2. Propagate trace context across service calls.
3. Export traces to backend (Jaeger, Zipkin). 4. Create service dependency map.
5. Set up trace-based alerting.
## Constraints
- Sample rate configurable. Always sample errors. Keep overhead < 1% latency.
## Success Criteria
- Traces flow across services. Dependency map accurate. Errors always sampled.
```
