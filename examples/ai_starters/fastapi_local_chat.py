"""FastAPI local AI chat web app (no cloud API)."""

from functools import lru_cache

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from examples.ai_starters.local_model_chat import LocalChatModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@lru_cache(maxsize=1)
def get_model() -> LocalChatModel:
    return LocalChatModel()


app = FastAPI(title="Local AI Chat")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>Local AI Chat</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        max-width: 760px;
        margin: 2rem auto;
        padding: 1rem;
      }
      textarea, button { width: 100%; font-size: 1rem; }
      textarea { min-height: 100px; margin-bottom: 0.75rem; }
      #out {
        white-space: pre-wrap;
        background: #f6f8fa;
        border-radius: 8px;
        padding: 1rem;
        min-height: 140px;
      }
    </style>
  </head>
  <body>
    <h1>Local AI Chat (FastAPI)</h1>
    <textarea id=\"msg\" placeholder=\"Type your prompt...\"></textarea>
    <button onclick=\"sendMsg()\">Send</button>
    <h3>Response</h3>
    <div id=\"out\"></div>
    <script>
      async function sendMsg() {
        const message = document.getElementById('msg').value;
        const out = document.getElementById('out');
        out.textContent = 'Thinking...';

        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message })
        });

        if (!res.ok) {
          out.textContent = `Request failed: ${res.status}`;
          return;
        }

        const data = await res.json();
        out.textContent = data.reply;
      }
    </script>
  </body>
</html>
"""


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    reply = get_model().ask(req.message)
    return ChatResponse(reply=reply)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "examples.ai_starters.fastapi_local_chat:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
