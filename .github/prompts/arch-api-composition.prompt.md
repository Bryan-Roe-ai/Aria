```prompt
---
agent: agent
description: "Implement API composition pattern for aggregation"
---
# API Composition
## Task
Implement API composition for aggregating multiple service responses.
## Requirements
1. Define composer endpoint that calls multiple backends. 2. Execute independent calls in parallel.
3. Handle partial failures gracefully. 4. Merge responses into unified format.
5. Cache aggregated responses when appropriate.
## Constraints
- Parallel execution for independent calls. Timeout for slow backends. Return partial on failure.
## Success Criteria
- Responses aggregated correctly. Parallel calls faster. Partial failures handled.
```
