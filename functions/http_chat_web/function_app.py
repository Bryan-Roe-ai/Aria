import sys
from pathlib import Path

import azure.functions as func

from shared.http_utils import serve_static_file

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

app = func.FunctionApp()


@app.route(route="chat-web", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def serve_chat_web(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the chat web interface"""
    html_path = REPO_ROOT / "apps" / "chat" / "index.html"
    content, status_code, headers = serve_static_file(html_path, "text/html", use_cache_headers=True)

    return func.HttpResponse(content, status_code=status_code, mimetype="text/html", headers=headers)


@app.route(route="chat-web/chat.js", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def serve_chat_js(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the chat JavaScript file"""
    js_path = REPO_ROOT / "apps" / "chat" / "chat.js"
    content, status_code, headers = serve_static_file(js_path, "application/javascript", use_cache_headers=True)

    return func.HttpResponse(
        content,
        status_code=status_code,
        mimetype="application/javascript",
        headers=headers,
    )


@app.route(route="chat-web/static/agi_stream_utils.js", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def serve_agi_stream_utils(req: func.HttpRequest) -> func.HttpResponse:
    """Serve AGI SSE parsing utilities for chat-web clients."""
    js_path = REPO_ROOT / "apps" / "chat" / "static" / "agi_stream_utils.js"
    content, status_code, headers = serve_static_file(js_path, "application/javascript", use_cache_headers=True)

    return func.HttpResponse(
        content,
        status_code=status_code,
        mimetype="application/javascript",
        headers=headers,
    )
