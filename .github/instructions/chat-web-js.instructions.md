```instructions
---
name: "Chat-Web-JS"
description: "Guidance for web/chat-web/ JavaScript SSE consumer and TTS playback"
applyTo: "web/chat-web/**/*.js"
---
# Chat Web – JavaScript

- `web/chat-web/chat.js` is the SSE streaming consumer for the Aria chat frontend.
- SSE protocol: connect to `/api/chat`, read `data: {json}` lines, extract `content`/delta, render incrementally.
- Sentinel: `data: [DONE]` means the stream is complete — stop reading and finalize the response.
- Handle partial chunks: buffer incomplete lines and parse only complete `data:` entries.
- Reconnection: implement exponential backoff on connection drops.
- TTS: `/api/tts` returns `{ audio_base64, format }`; decode and play via `AudioContext` or `<audio>` element.
- Use `const`/`let` (no `var`), `async/await`, and structured error handling.
- Never store tokens or API keys in JS; all auth flows happen server-side.
- Ensure all chat UI elements are keyboard-accessible with ARIA labels.
- Test against `func host start` locally; check `/api/ai/status` before debugging streaming issues.
```
