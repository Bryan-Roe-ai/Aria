```prompt
---
agent: agent
description: "Implement API event streaming with server-sent events"
---
# API Event Streaming
## Task
Implement real-time event streaming via SSE.
## Requirements
1. Set Content-Type to text/event-stream. 2. Format events as `data: {json}\n\n`.
3. Send heartbeat every 30s to keep connection. 4. Support event types and IDs for filtering.
5. Handle client reconnection with Last-Event-ID.
## Constraints
- Follow Aria SSE convention. End stream with `[DONE]`. Buffer responses appropriately.
## Success Criteria
- Events stream in real-time. Heartbeats keep connection. Reconnection resumes correctly.
```
