#!/usr/bin/env python3
"""Minimal MCP server that exposes LM Studio tools to GitHub Copilot Chat.

This server bridges Copilot MCP tool calls to an OpenAI-compatible LM Studio
endpoint defined by LMSTUDIO_BASE_URL.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "lmstudio-server"
SERVER_VERSION = "1.0.0"
DEFAULT_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_TIMEOUT_SECONDS = 30


def _base_url() -> str:
    return os.getenv("LMSTUDIO_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _default_model() -> str:
    return os.getenv("LMSTUDIO_MODEL", "")


def _json_response(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _http_json(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{_base_url()}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    timeout = int(os.getenv("LMSTUDIO_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = exc.reason
        raise RuntimeError(f"LM Studio HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Cannot connect to LM Studio at {_base_url()} ({exc.reason})"
        ) from exc


def _tool_result(text: str, structured: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "content": [{"type": "text", "text": text}],
        "isError": False,
    }
    if structured is not None:
        result["structuredContent"] = structured
    return result


def _tool_error(msg_id: Any, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "content": [{"type": "text", "text": message}],
            "isError": True,
        },
    }


def _initialize_response(msg_id: Any) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        },
    }


def _tools_list_response(msg_id: Any) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "tools": [
                {
                    "name": "lmstudio_status",
                    "description": "Check LM Studio connectivity and current configuration.",
                    "inputSchema": {"type": "object", "properties": {}, "required": []},
                },
                {
                    "name": "lmstudio_list_models",
                    "description": "List models available from the configured LM Studio endpoint.",
                    "inputSchema": {"type": "object", "properties": {}, "required": []},
                },
                {
                    "name": "lmstudio_chat",
                    "description": "Send a one-shot chat request to LM Studio and return the assistant response.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "User prompt to send to LM Studio.",
                            },
                            "system": {
                                "type": "string",
                                "description": "Optional system instruction.",
                            },
                            "model": {
                                "type": "string",
                                "description": "Optional model override. Defaults to LMSTUDIO_MODEL or first available model.",
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Optional generation temperature.",
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "Optional output token limit.",
                            },
                        },
                        "required": ["prompt"],
                    },
                },
            ]
        },
    }


def _status() -> dict[str, Any]:
    payload = _http_json("GET", "/models")
    models = payload.get("data", [])
    return {
        "base_url": _base_url(),
        "configured_model": _default_model(),
        "reachable": True,
        "model_count": len(models),
        "models": [m.get("id", "") for m in models],
    }


def _list_models() -> dict[str, Any]:
    payload = _http_json("GET", "/models")
    models = payload.get("data", [])
    return {
        "base_url": _base_url(),
        "models": [
            {
                "id": model.get("id", ""),
                "object": model.get("object", "model"),
                "owned_by": model.get("owned_by", "unknown"),
            }
            for model in models
        ],
    }


def _select_model(requested_model: str | None) -> str:
    if requested_model:
        return requested_model
    if _default_model():
        return _default_model()
    payload = _http_json("GET", "/models")
    models = payload.get("data", [])
    if not models:
        raise RuntimeError("LM Studio returned no models.")
    return models[0].get("id", "")


def _chat(arguments: dict[str, Any]) -> dict[str, Any]:
    prompt = str(arguments.get("prompt", "")).strip()
    if not prompt:
        raise RuntimeError("'prompt' is required.")

    messages: list[dict[str, str]] = []
    system = str(arguments.get("system", "")).strip()
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body: dict[str, Any] = {
        "model": _select_model(arguments.get("model")),
        "messages": messages,
        "stream": False,
    }
    if "temperature" in arguments:
        body["temperature"] = arguments["temperature"]
    if "max_tokens" in arguments:
        body["max_tokens"] = arguments["max_tokens"]

    payload = _http_json("POST", "/chat/completions", body)
    choices = payload.get("choices", [])
    if not choices:
        raise RuntimeError("LM Studio returned no choices.")
    message = choices[0].get("message", {})
    content = (message.get("content") or "").strip()
    # Reasoning models (e.g. nemotron, ministral-reasoning) may return an empty
    # content field when max_tokens is exhausted by the chain-of-thought.
    # Fall back to reasoning_content so the caller always gets something useful.
    if not content:
        content = (message.get("reasoning_content") or "").strip()
    return {
        "model": payload.get("model", body["model"]),
        "response": content,
        "finish_reason": choices[0].get("finish_reason", "unknown"),
        "usage": payload.get("usage", {}),
    }


def _handle_tool_call(msg_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {}) or {}
    try:
        if tool_name == "lmstudio_status":
            status = _status()
            text = (
                f"LM Studio reachable at {status['base_url']} with {status['model_count']} model(s): "
                + ", ".join(status["models"])
            )
            return {"jsonrpc": "2.0", "id": msg_id, "result": _tool_result(text, status)}
        if tool_name == "lmstudio_list_models":
            models = _list_models()
            model_ids = [m["id"] for m in models["models"]]
            text = f"LM Studio models at {models['base_url']}: " + ", ".join(model_ids)
            return {"jsonrpc": "2.0", "id": msg_id, "result": _tool_result(text, models)}
        if tool_name == "lmstudio_chat":
            chat = _chat(arguments)
            text = chat["response"] or "LM Studio returned an empty response."
            return {"jsonrpc": "2.0", "id": msg_id, "result": _tool_result(text, chat)}
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
        }
    except Exception as exc:
        return _tool_error(msg_id, f"LM Studio tool error: {exc}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue

        method = msg.get("method", "")
        msg_id = msg.get("id")

        if method == "initialize":
            resp = _initialize_response(msg_id)
        elif method == "tools/list":
            resp = _tools_list_response(msg_id)
        elif method == "tools/call":
            resp = _handle_tool_call(msg_id, msg.get("params", {}))
        elif method == "notifications/initialized":
            continue
        else:
            if msg_id is None:
                continue
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

        print(_json_response(resp), flush=True)


if __name__ == "__main__":
    main()
