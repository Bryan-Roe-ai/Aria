from __future__ import annotations

from function_app_domains.access import require_access


def agi_analyze(req, ctx):
    unauthorized = require_access(req, ctx, "agi")
    if unauthorized is not None:
        return unauthorized

    try:
        req_body, req_err = ctx.validate_request(req, ctx.AGI_ANALYZE_SCHEMA)
        if req_err:
            raise ValueError(req_err)
        query = ctx._extract_agi_query_from_request(req_body)
        provider, provider_choice = ctx._create_agi_provider_for_api(
            model_override=req_body.get("model"),
            temperature=req_body.get("temperature"),
            max_output_tokens=req_body.get("max_output_tokens"),
            verbose=bool(req_body.get("verbose", False)),
        )
        analysis = provider._analyze_query(query)
        selected_agent, agent_score = provider._select_agent(analysis)
        payload = {
            "status": "ok",
            "query": query,
            "analysis": analysis,
            "routing": {"selected_agent": selected_agent, "agent_score": float(agent_score)},
            "provider": ctx._agi_provider_metadata(provider, provider_choice),
        }
        return ctx.func.HttpResponse(
            ctx.json.dumps(payload),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except ValueError as exc:
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": f"Validation error: {exc}"}),
            status_code=400,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except RuntimeError as exc:
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": f"Configuration error: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("agi/analyze error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": str(exc)}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def agi_status(req, ctx):
    unauthorized = require_access(req, ctx, "agi")
    if unauthorized is not None:
        return unauthorized

    try:
        provider = None
        provider_choice = None
        agent_tools: dict[str, list[str]] = {}
        summary = {
            "total_reasoning_chains": 0,
            "active_goals": [],
            "learned_patterns_count": 0,
            "top_learned_patterns": [],
            "conversation_length": 0,
            "last_agent_used": None,
            "last_agent_score": None,
            "available_agents": [],
        }
        available = ctx.create_agi_provider is not None
        if available:
            provider, provider_choice = ctx._create_agi_provider_for_api()
            summary = provider.get_reasoning_summary()

        try:
            from agi_provider import _AGENT_REGISTRY

            for agent_name, config in _AGENT_REGISTRY.items():
                tools = config.get("tools") if isinstance(config, dict) else None
                if not isinstance(tools, list) or not tools:
                    continue
                tool_names = [str(tool.get("name")) for tool in tools if isinstance(tool, dict) and tool.get("name")]
                if tool_names:
                    agent_tools[str(agent_name)] = sorted(set(tool_names))
        except Exception:
            agent_tools = {}

        agent_tools["mcp-agi"] = sorted(["agi_analyze", "agi_reason", "agi_stream"])
        provider_meta = {"name": "agi", "base_provider": None, "base_model": None, "wrapper_model": None}
        if available:
            provider_meta = ctx._agi_provider_metadata(provider, provider_choice)

        payload = {
            "status": "ok",
            "available": available,
            "provider": provider_meta,
            "reasoning": summary,
            "agent_tools": agent_tools,
            "backends": ctx.build_agi_backend_status(provider),
            "endpoints": [
                "/api/agi/analyze",
                "/api/agi/reason",
                "/api/agi/stream",
                "/api/agi/status",
                "/api/agi/persistence",
            ],
        }
        return ctx.func.HttpResponse(
            ctx.json.dumps(payload),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("agi/status error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": str(exc)}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def agi_reason(req, ctx):
    unauthorized = require_access(req, ctx, "agi")
    if unauthorized is not None:
        return unauthorized

    try:
        req_body, req_err = ctx.validate_request(req, ctx.AGI_REASON_SCHEMA)
        if req_err:
            raise ValueError(req_err)
        query = ctx._extract_agi_query_from_request(req_body)
        messages = req_body.get("messages")
        if isinstance(messages, list) and messages:
            messages = ctx._sanitize_chat_messages(messages)
        else:
            messages = [{"role": "user", "content": query}]

        provider, provider_choice = ctx._create_agi_provider_for_api(
            model_override=req_body.get("model"),
            temperature=req_body.get("temperature"),
            max_output_tokens=req_body.get("max_output_tokens"),
            verbose=bool(req_body.get("verbose", False)),
        )
        goals = req_body.get("goals", [])
        if isinstance(goals, list):
            for goal in goals:
                if isinstance(goal, str) and goal.strip():
                    provider.set_goal(goal)

        result = provider.complete(messages, stream=False)
        if hasattr(result, "__iter__") and not isinstance(result, str):
            result = "".join(result)

        payload = {
            "status": "ok",
            "query": query,
            "response": str(result),
            "provider": ctx._agi_provider_metadata(provider, provider_choice),
        }
        if bool(req_body.get("include_reasoning_summary", True)):
            payload["reasoning"] = provider.get_reasoning_summary()

        return ctx.func.HttpResponse(
            ctx.json.dumps(payload),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except ValueError as exc:
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": f"Validation error: {exc}"}),
            status_code=400,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except RuntimeError as exc:
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": f"Configuration error: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("agi/reason error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": str(exc)}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def agi_stream(req, ctx):
    unauthorized = require_access(req, ctx, "agi")
    if unauthorized is not None:
        return unauthorized

    try:
        req_body, req_err = ctx.validate_request(req, ctx.AGI_STREAM_SCHEMA)
        if req_err:
            raise ValueError(req_err)
        query = ctx._extract_agi_query_from_request(req_body)
        messages = req_body.get("messages")
        if isinstance(messages, list) and messages:
            messages = ctx._sanitize_chat_messages(messages)
        else:
            messages = [{"role": "user", "content": query}]

        provider, provider_choice = ctx._create_agi_provider_for_api(
            model_override=req_body.get("model"),
            temperature=req_body.get("temperature"),
            max_output_tokens=req_body.get("max_output_tokens"),
            verbose=bool(req_body.get("verbose", False)),
        )
        goals = req_body.get("goals", [])
        if isinstance(goals, list):
            for goal in goals:
                if isinstance(goal, str) and goal.strip():
                    provider.set_goal(goal)

        generator = provider.complete(messages, stream=True)

        def _sse_iterable():
            try:
                prelude = ctx._agi_provider_metadata(provider, provider_choice)
                yield (f"event: meta\n" f"data: {ctx.json.dumps(prelude)}\n\n").encode("utf-8")
                for chunk in generator:
                    if not chunk:
                        continue
                    payload = ctx.json.dumps({"delta": ctx._normalize_agi_stream_delta(chunk)})
                    yield (f"data: {payload}\n\n").encode("utf-8")
                yield b"data: [DONE]\n\n"
            except Exception as exc:
                yield (f"event: error\n" f"data: {ctx.json.dumps({'error': str(exc)})}\n\n").encode("utf-8")
                yield b"data: [DONE]\n\n"

        return ctx._sse_response(_sse_iterable(), status_code=200)
    except ValueError as exc:
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": f"Validation error: {exc}"}),
            status_code=400,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except RuntimeError as exc:
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": f"Configuration error: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("agi/stream error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": str(exc)}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def agi_persistence(req, ctx):
    unauthorized = require_access(
        req,
        ctx,
        "agi",
        extra_token_env_names=("QAI_AGI_PERSIST_READ_TOKEN",),
        extra_header_names=("X-AGI-AUDIT-TOKEN",),
    )
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("AGI persistence endpoint invoked")
    try:
        limit = 50
        try:
            if hasattr(req, "params") and req.params.get("limit"):
                limit = int(req.params.get("limit"))
            else:
                try:
                    limit = int(req.get_json().get("limit", limit))
                except Exception:
                    pass
        except Exception:
            limit = 50
        limit = max(1, min(limit, 500))

        sqlite_path = ctx.os.getenv("QAI_AGI_PERSIST_DB") or ctx.os.getenv("QAI_AGI_PERSIST_SQLITE")
        jsonl_path = ctx.os.getenv("QAI_AGI_PERSIST_PATH")
        jsonl_enabled = ctx.os.getenv("QAI_AGI_PERSIST", "true").lower() in ("1", "true", "yes")
        default_jsonl_path = ctx._default_agi_persist_jsonl_path()

        if sqlite_path:
            try:
                from shared.agi_persistence_sqlite import SQLiteAGIPersistence

                backend = SQLiteAGIPersistence(sqlite_path)
                entries = backend.read_last(limit)
                backend.close()
                return ctx.func.HttpResponse(
                    ctx.json.dumps({"status": "ok", "backend": "sqlite", "entries": entries}, default=str),
                    status_code=200,
                    mimetype="application/json",
                    headers=ctx.create_cors_response_headers(),
                )
            except Exception as exc:
                ctx.logging.exception("AGI persistence sqlite read error: %s", exc)
                return ctx.func.HttpResponse(
                    ctx.json.dumps({"status": "error", "error": str(exc)}),
                    status_code=500,
                    mimetype="application/json",
                    headers=ctx.create_cors_response_headers(),
                )

        path = jsonl_path or default_jsonl_path
        if jsonl_path or jsonl_enabled or ctx.os.path.exists(path) or not sqlite_path:
            try:
                entries = []
                if ctx.os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as handle:
                        lines = handle.read().splitlines()
                    for line in lines[-limit:]:
                        try:
                            entries.append(ctx.json.loads(line))
                        except Exception:
                            entries.append({"raw": line})
                return ctx.func.HttpResponse(
                    ctx.json.dumps(
                        {
                            "status": "ok",
                            "backend": "jsonl",
                            "path": path,
                            "configured": bool(jsonl_path or jsonl_enabled or ctx.os.path.exists(path)),
                            "entries": entries,
                        },
                        default=str,
                    ),
                    status_code=200,
                    mimetype="application/json",
                    headers=ctx.create_cors_response_headers(),
                )
            except Exception as exc:
                ctx.logging.exception("AGI persistence jsonl read error: %s", exc)
                return ctx.func.HttpResponse(
                    ctx.json.dumps({"status": "error", "error": str(exc)}),
                    status_code=500,
                    mimetype="application/json",
                    headers=ctx.create_cors_response_headers(),
                )

        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": "AGI persistence not configured"}),
            status_code=404,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.exception("agi/persistence unexpected error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "error": str(exc)}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
