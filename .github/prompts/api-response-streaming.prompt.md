```prompt
---
agent: agent
description: "Implement API response streaming for large datasets"
---
# API Response Streaming
## Task
Implement response streaming for large dataset delivery.
## Requirements
1. Use chunked transfer encoding. 2. Stream database results without loading all in memory.
3. Support NDJSON (newline-delimited JSON) format. 4. Set appropriate Content-Type header.
5. Handle client disconnection gracefully.
## Constraints
- Stream from cursor/iterator. Don't materialize full result set. Handle backpressure.
## Success Criteria
- Large responses stream efficiently. Memory usage constant. Client disconnection handled.
```
