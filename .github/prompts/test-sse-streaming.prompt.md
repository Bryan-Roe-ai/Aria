```prompt
---
agent: agent
description: "Test SSE streaming endpoints for chunk-by-chunk delivery"
---
# SSE Streaming Tests
## Task
Write tests for Server-Sent Events streaming endpoints.
## Requirements
1. Verify `Content-Type: text/event-stream`.
2. Test chunk format (`data: {json}\n\n`).
3. Test `[DONE]` sentinel at stream end.
4. Test stream interruption and recovery.
5. Test keep-alive and connection timeout.
## Constraints
- Follow Aria SSE conventions (`data: {json}` + `[DONE]`). Test with async HTTP client.
## Success Criteria
- SSE format correct. Streams complete with `[DONE]`. Interruption handled gracefully.
```
