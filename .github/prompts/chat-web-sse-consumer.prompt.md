```prompt
---
agent: agent
description: "Build or fix the chat-web frontend SSE streaming consumer"
---
# Chat Web SSE Consumer

## Task
Implement or debug the SSE streaming consumer in the chat-web frontend.

## Context
- Frontend: `web/chat-web/chat.js`, `web/chat-web/index.html`, `web/chat-web/aria.html`
- SSE endpoint: `/api/chat` streams `data: {json}` lines with `content`/delta fields
- Sentinel: `data: [DONE]` signals stream end
- TTS: `/api/tts` returns `audio_base64` and `format` (mp3/wav)
- Backend status: `/api/ai/status`

## Requirements
1. Parse SSE `data:` lines correctly; extract `content` or delta from JSON.
2. Handle `[DONE]` sentinel to finalize the response.
3. Implement reconnection logic for dropped connections.
4. Render streamed tokens incrementally in the UI.
5. Handle TTS playback if audio is enabled.

## Constraints
- No secrets or tokens in client-side JS.
- Use `const`/`let`, `async/await`, proper error handling.
- Ensure accessibility (ARIA labels, keyboard nav).
- Functions host must be running for testing (`func host start`).

## Success Criteria
- SSE stream renders tokens in real-time without corruption.
- `[DONE]` stops rendering cleanly.
- Connection drops handled gracefully with retry.
- TTS plays audio correctly when enabled.
```
