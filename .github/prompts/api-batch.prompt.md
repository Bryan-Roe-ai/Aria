```prompt
---
agent: agent
description: "Implement API batch endpoints for bulk operations"
---
# API Batch Endpoints
## Task
Implement batch endpoints for bulk API operations.
## Requirements
1. Accept array of operations in single request.
2. Process items independently (partial success allowed).
3. Return per-item results with status.
4. Set maximum batch size limit.
5. Support async batch processing for large sets.
## Constraints
- Max batch size 100. Return 207 Multi-Status for partial results. No all-or-nothing.
## Success Criteria
- Batch operations process independently. Per-item results returned. Size limits enforced.
```
