```prompt
---
agent: agent
description: "Implement API background job processing with status polling"
---
# API Background Jobs
## Task
Implement async background job processing with status polling.
## Requirements
1. Return 202 Accepted with job ID for long operations.
2. Provide `GET /jobs/{id}` for status polling.
3. Return progress percentage and status (pending/running/completed/failed).
4. Support job cancellation via DELETE.
5. Clean up completed jobs after retention period.
## Constraints
- Never block API requests for long operations. Store job state. Implement timeouts.
## Success Criteria
- Long operations return immediately with job ID. Status polling works. Jobs can be cancelled.
```
