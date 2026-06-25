"""
Local Developer Adapter for Azure Functions endpoints

This tiny adapter lets you run selected Azure Functions handlers locally without
needing the Azure Functions Core Tools host. It exposes the status, routes, AGI,
and chat-web static endpoints used by local health checks.
needing the Azure Functions Core Tools host. It exposes ``GET /api/ai/status``
and ``GET /api/agi/status`` for local health checks.

Usage:
  python local_dev_adapter.py
  python local_dev_adapter.py --port 7072
  python local_dev_adapter.py --check

Design notes:
  python local_dev_adapter.py
  python local_dev_adapter.py --port 7072
  python local_dev_adapter.py --check

Design notes:
Design notes:
- Imports the `function_app` module and calls `ai_status()` directly.
- Uses Flask when available, but falls back to a stdlib HTTP server so strict
    integration smoke checks can run in minimal Python environments.
"""

from __future__ import annotations
import argparse
import json
import argparse
import json
import logging
import os
import sys
import types
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from shared.local_settings import apply_local_settings

try:
    from flask import Flask, Response, make_response, request

    HAS_FLASK = True
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal envs
    Flask = None  # type: ignore[assignment]
    Response = Any  # type: ignore[assignment]
    make_response = None  # type: ignore[assignment]
    HAS_FLASK = False

logger = logging.getLogger(__name__)

# Ensure repo modules are importable when running from the repo root.


def _safe_log_label(value: str) -> str:
    """Strip control chars from user-influenced values before logging."""
    return str(value).split("?", 1)[0].replace("\n", "").replace("\r", "")[:120]


# Ensure repo modules are importable when running from the repo root.
def _safe_log_label(value: str) -> str:
    """Strip control chars from user-influenced values before logging."""
    return str(value).split("?", 1)[0].replace("\n", "").replace("\r", "")[:120]


# Ensure repo modules are importable when running from the repo root.
sys.path.insert(0, str(repo_root / "ai-projects" / "chat-cli" / "src"))
sys.path.insert(0, str(repo_root / "ai-projects" / "quantum-ml" / "src"))
sys.path.insert(0, str(repo_root / "scripts"))
sys.path.insert(0, str(repo_root))


def _load_env_file() -> None:
    """Load local dev settings early so provider selection sees them."""
    apply_local_settings()

    env_file = repo_root / ".env"
    if not env_file.exists():
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(env_file, override=False)
    except ImportError:
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    if key not in os.environ:
                        os.environ[key] = val


def _install_azure_functions_shim() -> Any:
    """Install a lightweight azure.functions shim for local development."""
    logger.debug(
        "azure.functions not found; installing lightweight shim for local dev adapter"
    logger.debug(
        "azure.functions not found; installing lightweight shim for local dev adapter")
    fake_mod=types.ModuleType("azure.functions")
        ANONYMOUS="ANONYMOUS"

    class HttpRequest:  # minimal request placeholder with helpful helpers
        def __init__(
            self,
            method: str="GET",
            url: str="/",
            params: dict | None=None,
            headers: dict | None=None,
            body: Any=None,
            route_params: dict | None=None,
        ):
            self.method=method
            self.url=url
            self.params=params or {}
            self.route_params=route_params or {}
            self.headers={k.lower(): v for k, v in (headers or {}).items()}
            if isinstance(body, bytes):
                self._body=body
            elif isinstance(body, str):
                self._body=body.encode("utf-8")
            elif body is None:
                self._body=b""
            else:
                try:
                    self._body=json.dumps(body).encode("utf-8")
                except Exception:
                    self._body=str(body).encode("utf-8")
            self._json_cache=None

        def get_body(self) -> bytes:
            return self._body

        def get_json(self, force: bool=False):
            if self._json_cache is not None and not force:
                return self._json_cache
            try:
                text=self._body.decode("utf-8")
                parsed=json.loads(text) if text else {}
                self._json_cache=parsed
                return parsed
            except Exception as e:
                logger.debug("HttpRequest.get_json failed: %s", e)
                raise ValueError("Failed to parse JSON body") from e

    class HttpResponse:
        def __init__(
            self,
            body=b"",
            status_code: int=200,
            mimetype: str | None=None,
            headers: dict | None=None,
        ):
            if isinstance(body, str):
                self._body=body.encode("utf-8")
            elif isinstance(body, bytes):
                self._body=body
            else:
                try:
                    self._body=json.dumps(body).encode("utf-8")
                except Exception:
                    self._body=str(body).encode("utf-8")
            self.status_code=status_code
            self.mimetype=mimetype
            self.headers=headers or {}

        def get_body(self):
            return self._body

    class FunctionApp:
        def __init__(self):
            self._routes=[]

        def route(self, *args, **kwargs):
            def decorator(fn):
                try:
                    fn.__qai_route__={"args": args, "kwargs": kwargs}
                except Exception:
                    pass
                return fn

            return decorator

    fake_mod.AuthLevel=AuthLevel
    fake_mod.HttpRequest=HttpRequest
    fake_mod.HttpResponse=HttpResponse
    fake_mod.FunctionApp=FunctionApp

    azure_pkg=sys.modules.setdefault("azure", types.ModuleType("azure"))
    if not hasattr(azure_pkg, "__path__"):
        azure_pkg.__path__=[]  # type: ignore[attr-defined]
    setattr(azure_pkg, "functions", fake_mod)
    sys.modules["azure.functions"]=fake_mod
    return fake_mod.HttpResponse


_load_env_file()

try:
    from azure.functions import HttpResponse as AzureHttpResponse  # type: ignore
except ModuleNotFoundError:
    AzureHttpResponse=_install_azure_functions_shim()

# Import function_app only after sys.path, env, and shim setup.


    resp: AzureHttpResponse,
) -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:

    resp: AzureHttpResponse,


) -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:


def _get_function_app() -> Any:
    """Import function_app after sys.path, env, and azure shim setup."""
    import function_app as fa

    return fa


def _azure_response_parts(
    """Import function_app after sys.path, env, and azure shim setup."""
    import function_app as fa

    return fa


def _azure_response_parts(
    body_bytes=resp.get_body()
    # Ensure bytes
    if not isinstance(body_bytes, (bytes, bytearray)):
        try:
            body_bytes = str(body_bytes).encode("utf-8")
        except Exception:
            body_bytes = b""

    mimetype = getattr(resp, "mimetype", None)
    headers = dict(getattr(resp, "headers", None) or {})
    if not mimetype:
        content_type = headers.get(
            "Content-Type") or headers.get("content-type")
        if content_type:
            mimetype = content_type
        content_type = headers.get(
            "Content-Type") or headers.get("content-type")
            try:
                json.loads(body_bytes.decode("utf-8"))
                mimetype = "application/json"
            except Exception:
                mimetype = None

    status_code = int(getattr(resp, "status_code", 200))
    return bytes(body_bytes), status_code, mimetype, headers


def _azure_to_flask(resp: AzureHttpResponse) -> Response:
    """Convert an azure.functions.HttpResponse to a Flask Response."""
    body_bytes, status_code, mimetype, headers=_azure_response_parts(resp)

    flask_resp=make_response(body_bytes, status_code)
    if mimetype:
        flask_resp.mimetype = mimetype

    # Copy headers
    try:
        for k, v in headers.items():
            flask_resp.headers[k] = v
    except Exception:
        # best-effort fallback for unexpected header shapes
        logger.debug(
            "Unexpected header shape when converting azure HttpResponse to Flask Response")

    return flask_resp
        logger.debug(
            "Unexpected header shape when converting azure HttpResponse to Flask Response")
def get_ai_status_response() -> Tuple[Response, int]:
    """Call the function_app.ai_status handler and return a Flask response.

    ai_status() does not depend on incoming request data so we just call it
    handler_name: str,
    method: str,
    url: str,
    *,
    body: Any = None,
    headers: Optional[Dict[str, str]] = None,
) -> AzureHttpResponse:
    """Invoke a function_app HTTP handler with a minimal HttpRequest."""
    function_app = _get_function_app()
    handler = getattr(function_app, handler_name, None)
    if handler is None:
        raise RuntimeError(f"function_app.{handler_name} is not available")

    try:
        req_cls = getattr(function_app, "HttpRequest", None)
def _call_function_handler(handler_name: str, method: str, url: str) -> AzureHttpResponse:
    """Invoke a function_app HTTP handler with a minimal HttpRequest."""
    function_app = _get_function_app()
    handler = getattr(function_app, handler_name, None)
    if handler is None:
        raise RuntimeError(f"function_app.{handler_name} is not available")

    try:
        req_cls = getattr(function_app, "HttpRequest", None)
        req_cls = getattr(function_app, "HttpRequest", None)
        # Use shim's HttpRequest if available in sys.modules
    if isinstance(body, bytes):
        body_bytes = body
    elif isinstance(body, str):
        body_bytes = body.encode("utf-8")
    elif body is None:
        body_bytes = b""
    else:
        body_bytes = json.dumps(body).encode("utf-8")

    request_headers = dict(headers or {})
    if body is not None and not any(k.lower() == "content-type" for k in request_headers):
        request_headers["Content-Type"] = "application/json"

    request_kwargs = {
        "method": method,
        "url": url,
        "headers": request_headers,
        "params": {},
        "route_params": {},
        "body": body_bytes,
    }

    if req_cls is None or not hasattr(req_cls, "get_body"):
        try:
            from azure.functions import HttpRequest as ShimHttpRequest  # type: ignore

    request_kwargs = {"method": method, "url": url, "body": b""}

        try:
            from azure.functions import HttpRequest as ShimHttpRequest  # type: ignore
            fake_req = None
    else:
                fake_req = ShimHttpRequest(**request_kwargs)
            except TypeError:
                fake_req = ShimHttpRequest(
                    method=method, url=url, body=body_bytes)
        except Exception as exc:
            raise RuntimeError(
                "No HttpRequest implementation available for local dev adapter") from exc
    else:
        try:
            fake_req = req_cls(**request_kwargs)
        except TypeError:
            fake_req = req_cls(method=method, url=url, body=body_bytes)

    return handler(fake_req)


def get_ai_status_response() -> Tuple[Response, int]:
    """Call the function_app.ai_status handler and return a Flask response."""
    azure_resp = _call_function_handler("ai_status", "GET", "/api/ai/status")
    return _azure_to_flask(azure_resp)


def get_agi_status_response() -> Tuple[Response, int]:
    """Call function_app.agi_status and return a Flask response."""
    azure_resp = _call_function_handler("agi_status", "GET", "/api/agi/status")
    return _azure_to_flask(azure_resp)


def get_ai_routes_response() -> Tuple[Response, int]:
    """Call function_app.ai_routes and return a Flask response."""
    azure_resp = _call_function_handler("ai_routes", "GET", "/api/ai/routes")
    return _azure_to_flask(azure_resp)


def get_agi_analyze_response(payload: Dict[str, Any]) -> Tuple[Response, int]:
    """Call function_app.agi_analyze and return a Flask response."""
    azure_resp = _call_function_handler(
        "agi_analyze", "POST", "/api/agi/analyze", body=payload)
    return _azure_to_flask(azure_resp)


def get_agi_reason_response(payload: Dict[str, Any]) -> Tuple[Response, int]:
    """Call function_app.agi_reason and return a Flask response."""
    azure_resp = _call_function_handler(
        "agi_reason", "POST", "/api/agi/reason", body=payload)
    return _azure_to_flask(azure_resp)


def get_agi_stream_response(payload: Dict[str, Any]) -> Tuple[Response, int]:
    """Call function_app.agi_stream and return a Flask response."""
    azure_resp = _call_function_handler(
        "agi_stream", "POST", "/api/agi/stream", body=payload)
    return _azure_to_flask(azure_resp)


def get_agi_stream_utils_response() -> Tuple[Response, int]:
    """Call function_app.serve_agi_stream_utils and return a Flask response."""
    azure_resp = _call_function_handler(
        "serve_agi_stream_utils",
        "GET",
        "/api/chat-web/static/agi_stream_utils.js",
    )
    return _azure_to_flask(azure_resp)


def get_ai_status_parts() -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
                fake_req = ShimHttpRequest(**request_kwargs)
            except TypeError:
                fake_req = ShimHttpRequest(
                fake_req = ShimHttpRequest(method=method, url=url)
        except Exception as exc:
            raise RuntimeError(
                "No HttpRequest implementation available for local dev adapter"
            ) from exc
    else:
    else:
        try:
            fake_req = req_cls(**request_kwargs)
            fake_req = req_cls(method=method, url=url)


def get_ai_status_response() -> Tuple[Response, int]:
    """Call the function_app.ai_status handler and return a Flask response."""
    azure_resp = _call_function_handler("ai_status", "GET", "/api/ai/status")
    return _azure_to_flask(azure_resp)


def get_agi_status_response() -> Tuple[Response, int]:
    """Call function_app.agi_status and return a Flask response."""
    azure_resp = _call_function_handler("agi_status", "GET", "/api/agi/status")
    return _azure_to_flask(azure_resp)


    return _azure_to_flask(azure_resp)
    try:
        req = getattr(function_app, "HttpRequest", None)
    except Exception:
        req = None
    azure_resp = _call_function_handler("ai_status", "GET", "/api/ai/status")
    return _azure_response_parts(azure_resp)


def get_agi_status_parts() -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
    """Return / api/agi/status response components for non-Flask servers."""
    azure_resp = _call_function_handler("agi_status", "GET", "/api/agi/status")
    return _azure_response_parts(azure_resp)


def get_ai_routes_parts() -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
    """Return / api/ai/routes response components for non-Flask servers."""
    azure_resp = _call_function_handler("ai_routes", "GET", "/api/ai/routes")
    return _azure_response_parts(azure_resp)


def get_agi_analyze_parts(payload: Dict[str, Any]) -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
    """Return / api/agi/analyze response components for non-Flask servers."""
    azure_resp = _call_function_handler(
        "agi_analyze", "POST", "/api/agi/analyze", body=payload)
    return _azure_response_parts(azure_resp)


def get_agi_reason_parts(payload: Dict[str, Any]) -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
    """Return / api/agi/reason response components for non-Flask servers."""
    azure_resp = _call_function_handler(
        "agi_reason", "POST", "/api/agi/reason", body=payload)
    return _azure_response_parts(azure_resp)


def get_agi_stream_parts(payload: Dict[str, Any]) -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
    """Return / api/agi/stream response components for non-Flask servers."""
    azure_resp = _call_function_handler(
        "agi_stream", "POST", "/api/agi/stream", body=payload)
    return _azure_response_parts(azure_resp)


def get_agi_stream_utils_parts() -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
    """Return AGI stream utility JavaScript response components."""
    azure_resp = _call_function_handler(
        "serve_agi_stream_utils",
        "GET",
        "/api/chat-web/static/agi_stream_utils.js",
    )
    return _azure_response_parts(azure_resp)


def get_agi_status_parts() -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:
    """Return / api/agi/status response components for non-Flask servers."""
    azure_resp = _call_function_handler("agi_status", "GET", "/api/agi/status")
def get_agi_status_parts() -> Tuple[bytes, int, Optional[str], Dict[str, Any]]:

    azure_resp = _call_function_handler("agi_status", "GET", "/api/agi/status")

    @app.get("/api/ai/status")
    def ai_status_route():
        return get_ai_status_response()

    @app.get("/api/agi/status")
    def agi_status_route():
        return get_ai_status_response()

    return app


def run_stdlib_server(host: str = "0.0.0.0", port: int = 7071) -> None:
    @app.get("/api/agi/status")
    def agi_status_route():
        return get_agi_status_response()

    @app.get("/api/ai/routes")
    def ai_routes_route():
        return get_ai_routes_response()

    @app.post("/api/agi/analyze")
    def agi_analyze_route():
        return get_agi_analyze_response(request.get_json(silent=True) or {})

    @app.post("/api/agi/reason")
    def agi_reason_route():
        return get_agi_reason_response(request.get_json(silent=True) or {})

    @app.post("/api/agi/stream")
    def agi_stream_route():
        return get_agi_stream_response(request.get_json(silent=True) or {})

    @app.get("/api/chat-web/static/agi_stream_utils.js")
    def agi_stream_utils_route():
        return get_agi_stream_utils_response()

    return app


def run_stdlib_server(host: str = "0.0.0.0", port: int = 7071) -> None:
    """Serve selected local Functions endpoints using stdlib HTTP server."""

    class _Handler(BaseHTTPRequestHandler):
        def _read_json_body(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            if not raw:
                return {}
            parsed = json.loads(raw.decode("utf-8"))
            return parsed if isinstance(parsed, dict) else {}

        def _serve_parts(
            self,
            parts_fn,
            *,
            payload: Optional[Dict[str, Any]] = None,
        ) -> None:
            path = self.path.split("?", 1)[0]
            try:
                if payload is None:
                    body, status_code, mimetype, headers = parts_fn()
                else:
                    body, status_code, mimetype, headers = parts_fn(payload)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to build %s response: %s", _safe_log_label(path), exc)
                body = json.dumps({"error": str(exc)}).encode("utf-8")
        return get_ai_status_response()

    return app

    return app


def run_stdlib_server(host: str = "0.0.0.0", port: int = 7071) -> None:
def run_stdlib_server(host: str = "0.0.0.0", port: int = 7071) -> None:
    """Serve / api/ai/status using stdlib HTTP server(no Flask dependency)."""

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/api/ai/status":
                parts_fn = get_ai_status_parts
            elif path == "/api/agi/status":
                parts_fn = get_agi_status_parts
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"not found"}')
                return

            try:
                body, status_code, mimetype, headers = parts_fn()
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to build %s response: %s",
                                 _safe_log_label(path), exc)
                                 _safe_log_label(path), exc)
            self.send_response(status_code)
            sent_content_type = False
            if mimetype:
                self.send_header("Content-Type", str(mimetype))
                sent_content_type = True

            for key, value in headers.items():
                key_str = str(key)
                if key_str.lower() == "content-type":
                    if sent_content_type:
                        continue
                    sent_content_type = True
                self.send_header(key_str, str(value))

            if not sent_content_type:
                self.send_header("Content-Type", "application/json")
            self.end_headers()
        def log_message(self, _fmt: str, *_args: Any) -> None:

        def log_message(self, _fmt: str, *_args: Any) -> None:
            return

    logger.info("Starting stdlib local dev adapter on http://%s:%s", host, port)
        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/api/ai/status":
                parts_fn = get_ai_status_parts
            elif path == "/api/agi/status":
                parts_fn = get_agi_status_parts
            elif path == "/api/ai/routes":
                parts_fn = get_ai_routes_parts
            elif path == "/api/chat-web/static/agi_stream_utils.js":
                parts_fn = get_agi_stream_utils_parts
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"not found"}')
                return

            self._serve_parts(parts_fn)

        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path == "/api/agi/analyze":
                parts_fn = get_agi_analyze_parts
            elif path == "/api/agi/reason":
                parts_fn = get_agi_reason_parts
            elif path == "/api/agi/stream":
                parts_fn = get_agi_stream_parts
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"not found"}')
                return

            self._serve_parts(parts_fn, payload=self._read_json_body())

        def log_message(self, _fmt: str, *_args: Any) -> None:
        server.serve_forever()
    finally:
def check_status_endpoints() -> int:
    """Probe adapter handlers without starting an HTTP server."""
    probes = (
        server.server_close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse local adapter CLI arguments."""
        ("GET /api/agi/status", get_agi_status_parts),
    )
    errors: list[str] = []
    for label, parts_fn in probes:
        try:
            _body, status_code, _mimetype, _headers = parts_fn()
            if status_code != 200:
                errors.append(f"{label}: http {status_code}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{label}: {exc}")

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1

    print("ok: /api/ai/status, /api/agi/status")
    return 0


    """Parse local adapter CLI arguments."""

    default_host = os.getenv("LOCAL_DEV_ADAPTER_HOST", "0.0.0.0")
    default_port = int(os.getenv("LOCAL_DEV_ADAPTER_PORT", "7071"))
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
        server.server_close()


def check_status_endpoints() -> int:
    """Probe adapter handlers without starting an HTTP server."""
    probes = (
        ("GET /api/ai/status", get_ai_status_parts),
        ("GET /api/agi/status", get_agi_status_parts),
    )
    errors: list[str] = []
    for label, parts_fn in probes:
        try:
            _body, status_code, _mimetype, _headers = parts_fn()
            if status_code != 200:
                errors.append(f"{label}: http {status_code}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{label}: {exc}")

    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1

    print("ok: /api/ai/status, /api/agi/status")
    return 0
        description=(
            "Run the local dev adapter for GET /api/ai/status and GET /api/agi/status "
        description="Run the local /api/ai/status adapter without Azure Functions Core Tools.",
    )
    parser.add_argument(
        "--host",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python local_dev_adapter.py\n"
            "  python local_dev_adapter.py --port 7072\n"
            "  python local_dev_adapter.py --check\n"
            "  curl -s http://localhost:7071/api/agi/status | jq .backends\n"
        ),
    )
    parser.add_argument(
        "--host",
    parser.add_argument(
        description=(
            "Run the local dev adapter for GET /api/ai/status and GET /api/agi/status "
            "without Azure Functions Core Tools."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python local_dev_adapter.py\n"
            "  python local_dev_adapter.py --port 7072\n"
            "  python local_dev_adapter.py --check\n"
            "  curl -s http://localhost:7071/api/agi/status | jq .backends\n"
    parser.add_argument(
        "--port",
        type=int,
        default=default_port,
        help=f"Bind port for the local adapter (default: {default_port}).",
    )
        help=f"Bind port for the local adapter (default: {default_port}).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
        "--check",
        "--check",
        action="store_true",
        help="Probe /api/ai/status and /api/agi/status handlers and exit (no server).",
    )
    return parser.parse_args(argv)
        help=f"Bind port for the local adapter (default: {default_port}).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Probe /api/ai/status and /api/agi/status handlers and exit (no server).",
    print(
        f"Starting local dev adapter for /api/ai/status on http://{args.host}:{args.port}")

    if HAS_FLASK:
    if args.check:
        raise SystemExit(check_status_endpoints())

    print(f"Starting local dev adapter for /api/ai/status and /api/agi/status on http://{args.host}:{args.port}")
    if args.check:
    if args.check:
        raise SystemExit(check_status_endpoints())

    print(
        f"Starting local dev adapter for /api/ai/status and /api/agi/status on http://{args.host}:{args.port}")
    else:
        run_stdlib_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
