```chatagent
---
name: chat-web-frontend
description: Chat-web frontend development, SSE consumer implementation, and TTS integration.
---

# Chat Web Frontend Agent

## When to Use

- Building or fixing the chat-web HTML/JS frontend (`web/chat-web/`).
- Implementing SSE streaming consumers in `chat.js`.
- Debugging `data: {json}` parsing, `[DONE]` sentinel handling, or TTS playback.
- Updating `web/chat-web/index.html`, `aria.html`, or `start-backend.html`.

## Workflow

1. **Understand endpoints** — `/api/chat` (SSE streaming), `/api/chat-web`, `/api/tts` (audio synthesis).
2. **Read chat.js** — Understand current SSE parsing, message rendering, and error handling.
3. **Implement** — Follow SSE protocol: read `data: {json}` lines, extract `content`/delta, handle `[DONE]`.
4. **TTS** — Backend tries Azure Speech → pyttsx3 → gTTS; `/api/tts` returns `audio_base64` + `format`.
5. **Test** — Ensure Functions host is running (`func host start`), verify against `/api/ai/status`.

## Guardrails

- SSE parsing: skip `[DONE]` sentinel; handle partial chunks and reconnection.
- Never hardcode secrets in client-side JS; fetch config from backend APIs.
- Use `const`/`let` (no `var`), `async/await`, and proper error handling.
- Ensure the UI is accessible (ARIA labels, keyboard navigation, contrast).
- Recommended: `openai>=1.37.0` for streaming compatibility on backend.
```
