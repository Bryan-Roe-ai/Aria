from __future__ import annotations

from function_app_domains.access import require_access


def chat(req, ctx):
    unauthorized = require_access(req, ctx, "chat")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Chat function invoked")
    span_ctx = ctx._tracer.start_as_current_span("chat_request") if ctx._tracer is not None else None
    try:
        if span_ctx:
            span_ctx.__enter__()

        req_body = ctx._parse_json_object_body(req)
        messages = ctx._sanitize_chat_messages(req_body.get("messages", []))
        session_id = req_body.get("session_id")
        provider_choice = req_body.get("provider", ctx.os.getenv("QAI_PROVIDER", "auto"))
        model_override = req_body.get("model", ctx.os.getenv("QAI_LORA_MODEL"))
        temperature = req_body.get("temperature")
        max_output_tokens = req_body.get("max_output_tokens")
        max_context_tokens = req_body.get("max_context_tokens")
        system_prompt = req_body.get("system_prompt") or ctx._default_chat_system_prompt()
        guardrails_enabled = ctx._env_flag("QAI_AI_GUARDRAILS_ENABLED", True)
        ctx._AI_CAPABILITY_COUNTERS["chat_requests"] += 1

        user_message_content = next(
            (
                ctx._extract_text_content(message.get("content"))
                for message in reversed(messages)
                if message.get("role") == "user"
            ),
            None,
        )
        if guardrails_enabled and user_message_content:
            input_decision = ctx._ai_safety.validate_input(user_message_content)
            if not input_decision.allowed:
                ctx._AI_CAPABILITY_COUNTERS["safety_blocked_input"] += 1
                ctx._record_ai_capability_event(
                    "chat_input_blocked",
                    {
                        "provider_request": provider_choice,
                        "risk_level": input_decision.risk_level,
                        "reason": input_decision.reason,
                        "flags": list(getattr(input_decision, "flags", ()) or ()),
                    },
                )
                if span_ctx and hasattr(span_ctx, "__exit__"):
                    try:
                        span_ctx.__exit__(None, None, None)
                    except Exception:
                        pass
                return ctx.func.HttpResponse(
                    ctx.json.dumps(
                        {
                            "response": ctx._build_guardrail_fallback_text(),
                            "provider": "local",
                            "model": "safety-guardrail",
                            "memory_injected": 0,
                            "pruning": {
                                "original_tokens": 0,
                                "pruned_tokens": 0,
                                "removed_count": 0,
                                "budget": 0,
                                "reserve_output_tokens": 0,
                            },
                            "telemetry_span": bool(ctx._tracer),
                            "duration_ms": 0,
                            "cosmos_persisted": False,
                            "safety": {
                                "blocked": True,
                                "stage": "input",
                                "reason": input_decision.reason,
                                "risk_level": input_decision.risk_level,
                                "flags": list(getattr(input_decision, "flags", ()) or ()),
                            },
                        }
                    ),
                    status_code=200,
                    mimetype="application/json",
                    headers=ctx.create_cors_response_headers(),
                )

        memory_messages: list[dict] = []
        user_embedding = None
        if user_message_content:
            try:
                user_embedding = ctx.generate_embedding(user_message_content)
                similar = ctx.fetch_similar_messages(
                    user_embedding,
                    top_k=ctx._safe_int_env("QAI_MEMORY_TOP_K", 5),
                    session_id=session_id,
                    min_similarity=ctx._safe_float_env("QAI_MEMORY_MIN_SIMILARITY", 0.2),
                )
                ctx._AI_CAPABILITY_COUNTERS["memory_candidates"] += len(similar)
                for idx, similar_message in enumerate(similar):
                    memory_content = similar_message.get("content")
                    if memory_content and str(memory_content).strip():
                        memory_messages.append(
                            {
                                "role": "system",
                                "content": (
                                    f"[Memory #{idx + 1} | similarity={similar_message.get('similarity'):.3f}] "
                                    f"{memory_content}"
                                ),
                            }
                        )
            except Exception as exc:
                ctx.logging.warning("Memory retrieval failed: %s", exc)
                ctx._record_ai_capability_event(
                    "memory_retrieval_failed",
                    {"error": str(exc), "session_id": session_id},
                )

        if memory_messages:
            messages = memory_messages + messages
            ctx._AI_CAPABILITY_COUNTERS["memory_injected"] += len(memory_messages)

        provider, info = ctx._detect_provider_with_runtime_fallback(
            explicit=provider_choice,
            model_override=model_override,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        if (
            provider_choice
            and str(provider_choice).lower() != "auto"
            and str(info.name).lower() != str(provider_choice).lower()
        ):
            ctx._AI_CAPABILITY_COUNTERS["fallback_count"] += 1
            ctx._record_ai_capability_event(
                "provider_fallback",
                {
                    "requested_provider": str(provider_choice),
                    "resolved_provider": str(info.name),
                    "resolved_model": str(info.model),
                },
            )
        ctx.logging.info("Using provider: %s, model: %s", info.name, info.model)

        start_time = ctx.time.perf_counter()
        if ctx.prune_messages is None:
            raise RuntimeError(
                "prune_messages is unavailable. Chat CLI registry initialization failed. "
                "Check AI projects module availability and imports."
            )

        pruned_messages, stats, _ = ctx.prune_messages(
            messages=messages,
            provider=info.name,
            model=info.model,
            max_context_tokens=max_context_tokens,
            reserve_output_tokens=int(max_output_tokens) if max_output_tokens else 1024,
            system_prompt=system_prompt,
        )
        result = provider.complete(pruned_messages, stream=False)
        duration_ms = int((ctx.time.perf_counter() - start_time) * 1000)

        if hasattr(result, "__iter__") and not isinstance(result, str):
            result = "".join(result)
        result = str(result)
        if guardrails_enabled:
            output_decision = ctx._ai_safety.validate_output(result)
            if not output_decision.allowed:
                ctx._AI_CAPABILITY_COUNTERS["safety_blocked_output"] += 1
                ctx._record_ai_capability_event(
                    "chat_output_blocked",
                    {
                        "provider": info.name,
                        "model": info.model,
                        "risk_level": output_decision.risk_level,
                        "reason": output_decision.reason,
                        "flags": list(getattr(output_decision, "flags", ()) or ()),
                    },
                )
                result = ctx._build_guardrail_fallback_text()
        ctx._record_ai_latency(duration_ms)

        try:
            logs_dir = ctx.Path(__file__).resolve().parents[1] / "ai-projects" / "chat-cli" / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            timestamp = ctx.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = logs_dir / f"chat_{timestamp}_{session_id or 'anonymous'}.jsonl"
            with open(log_file, "a", encoding="utf-8") as handle:
                if user_message_content:
                    handle.write(
                        ctx.json.dumps(
                            {
                                "role": "user",
                                "content": user_message_content,
                                "timestamp": ctx.datetime.now().isoformat(),
                                "provider": info.name,
                                "model": info.model,
                            }
                        )
                        + "\n"
                    )
                handle.write(
                    ctx.json.dumps(
                        {
                            "role": "assistant",
                            "content": result,
                            "timestamp": ctx.datetime.now().isoformat(),
                            "provider": info.name,
                            "model": info.model,
                        }
                    )
                    + "\n"
                )
        except Exception as exc:
            ctx.logging.warning("Self-learning conversation logging failed: %s", exc)

        if ctx.log_chat_message_safe:
            try:
                if user_message_content:
                    user_log = ctx.log_chat_message_safe(
                        session_id=session_id,
                        provider=info.name,
                        model=info.model,
                        role="user",
                        content=user_message_content,
                        execution_time_ms=None,
                        finish_reason=None,
                    )
                    if user_log.get("success") and user_embedding:
                        try:
                            ctx.store_embedding(user_log.get("message_id"), user_embedding, model=info.model)
                        except Exception as exc:
                            ctx.logging.warning("Store embedding failed: %s", exc)
                ctx.log_chat_message_safe(
                    session_id=session_id,
                    provider=info.name,
                    model=info.model,
                    role="assistant",
                    content=result,
                    execution_time_ms=duration_ms,
                    finish_reason="stop",
                )
            except Exception as exc:
                ctx.logging.warning("Chat DB logging failed: %s", exc)

        cosmos_written = False
        user_id = session_id or "anonymous"
        if ctx.cosmos_client and ctx.os.getenv("QAI_ENABLE_COSMOS", "false").lower() == "true":
            try:
                if ctx.os.getenv("QAI_COSMOS_PERSIST_STRATEGY", "messages") == "messages":
                    last_user_msg = next(
                        (message for message in reversed(messages) if message.get("role") == "user"), None
                    )
                    if last_user_msg:
                        ctx.cosmos_client.record_chat_message(
                            user_id,
                            {"role": "user", "content": user_message_content, "timestamp": ctx.time.time()},
                            provider=info.name,
                            model=info.model,
                        )
                    ctx.cosmos_client.record_chat_message(
                        user_id,
                        {"role": "assistant", "content": result, "timestamp": ctx.time.time()},
                        provider=info.name,
                        model=info.model,
                    )
                    cosmos_written = True
                else:
                    ctx.cosmos_client.record_chat_session(user_id, messages, provider=info.name, model=info.model)
                    cosmos_written = True
            except Exception as exc:
                ctx.logging.warning("[cosmos] Persistence failed: %s", exc)

        response_data = {
            "response": result,
            "provider": info.name,
            "model": info.model,
            "memory_injected": len(memory_messages),
            "pruning": {
                "original_tokens": stats.original_tokens,
                "pruned_tokens": stats.pruned_tokens,
                "removed_count": stats.removed_count,
                "budget": stats.budget,
                "reserve_output_tokens": stats.reserve_output_tokens,
            },
            "telemetry_span": bool(ctx._tracer),
            "duration_ms": duration_ms,
            "cosmos_persisted": cosmos_written,
            "safety": {"enabled": guardrails_enabled},
        }

        if span_ctx and hasattr(span_ctx, "__exit__"):
            try:
                span = ctx.trace.get_current_span() if ctx._tracer else None  # type: ignore[union-attr]
                if span:
                    span.set_attribute("provider", info.name)
                    span.set_attribute("model", info.model)
                    span.set_attribute("duration_ms", duration_ms)
                    span.set_attribute("memory_injected", len(memory_messages))
                    span.set_attribute("cosmos_persisted", cosmos_written)
            finally:
                span_ctx.__exit__(None, None, None)

        return ctx.func.HttpResponse(
            ctx.json.dumps(response_data),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except ValueError as exc:
        ctx.logging.error("Validation error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Validation error: {exc}"}),
            status_code=400,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except RuntimeError as exc:
        ctx.logging.error("Runtime error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Configuration error: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Unexpected error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Internal server error: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def chat_options(req, ctx):
    return ctx.func.HttpResponse("", status_code=200, headers=ctx.create_cors_response_headers())


def chat_stream(req, ctx):
    unauthorized = require_access(req, ctx, "chat")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Chat stream function invoked")
    try:
        body = ctx._parse_json_object_body(req)
        messages = ctx._sanitize_chat_messages(body.get("messages", []))
        provider_choice = body.get("provider", "auto")
        model_override = body.get("model")
        temperature = body.get("temperature")
        max_output_tokens = body.get("max_output_tokens")
        max_context_tokens = body.get("max_context_tokens")
        system_prompt = body.get("system_prompt") or ctx._default_chat_system_prompt()
        guardrails_enabled = ctx._env_flag("QAI_AI_GUARDRAILS_ENABLED", True)
        ctx._AI_CAPABILITY_COUNTERS["chat_stream_requests"] += 1

        stream_user_content = next(
            (
                ctx._extract_text_content(message.get("content"))
                for message in reversed(messages)
                if message.get("role") == "user"
            ),
            None,
        )
        if guardrails_enabled and stream_user_content:
            input_decision = ctx._ai_safety.validate_input(stream_user_content)
            if not input_decision.allowed:
                ctx._AI_CAPABILITY_COUNTERS["safety_blocked_input"] += 1
                ctx._record_ai_capability_event(
                    "chat_stream_input_blocked",
                    {
                        "provider_request": provider_choice,
                        "risk_level": input_decision.risk_level,
                        "reason": input_decision.reason,
                        "flags": list(getattr(input_decision, "flags", ()) or ()),
                    },
                )

                def blocked_sse():
                    pre = {
                        "provider": "local",
                        "model": "safety-guardrail",
                        "memory_messages": 0,
                        "safety": {"blocked": True, "stage": "input"},
                    }
                    yield (f"event: meta\ndata: {ctx.json.dumps(pre)}\n\n").encode()
                    payload = ctx.json.dumps({"delta": ctx._build_guardrail_fallback_text()})
                    yield (f"data: {payload}\n\n").encode()
                    yield b"data: [DONE]\n\n"

                return ctx._sse_response(blocked_sse(), status_code=200)

        stream_memory_messages: list[dict] = []
        if stream_user_content:
            try:
                stream_embedding = ctx.generate_embedding(stream_user_content)
                similar_messages = ctx.fetch_similar_messages(
                    stream_embedding,
                    top_k=ctx._safe_int_env("QAI_MEMORY_TOP_K", 5),
                    session_id=body.get("session_id"),
                    min_similarity=ctx._safe_float_env("QAI_MEMORY_MIN_SIMILARITY", 0.2),
                )
                ctx._AI_CAPABILITY_COUNTERS["memory_candidates"] += len(similar_messages)
                for idx, similar_message in enumerate(similar_messages):
                    memory_content = similar_message.get("content")
                    if memory_content and str(memory_content).strip():
                        stream_memory_messages.append(
                            {
                                "role": "system",
                                "content": (
                                    f"[Memory #{idx + 1} | similarity={similar_message.get('similarity'):.3f}] "
                                    f"{memory_content}"
                                ),
                            }
                        )
            except Exception as exc:
                ctx.logging.warning("Stream memory retrieval failed: %s", exc)
                ctx._record_ai_capability_event(
                    "memory_stream_retrieval_failed",
                    {"error": str(exc), "session_id": body.get("session_id")},
                )
        if stream_memory_messages:
            messages = stream_memory_messages + messages
            ctx._AI_CAPABILITY_COUNTERS["memory_injected"] += len(stream_memory_messages)

        provider, info = ctx._detect_provider_with_runtime_fallback(
            explicit=provider_choice,
            model_override=model_override,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        if (
            provider_choice
            and str(provider_choice).lower() != "auto"
            and str(info.name).lower() != str(provider_choice).lower()
        ):
            ctx._AI_CAPABILITY_COUNTERS["fallback_count"] += 1
            ctx._record_ai_capability_event(
                "provider_fallback_stream",
                {
                    "requested_provider": str(provider_choice),
                    "resolved_provider": str(info.name),
                    "resolved_model": str(info.model),
                },
            )

        pruned_messages, stats, _ = ctx.prune_messages(
            messages=messages,
            provider=info.name,
            model=info.model,
            max_context_tokens=max_context_tokens,
            reserve_output_tokens=int(max_output_tokens) if max_output_tokens else 1024,
            system_prompt=system_prompt,
        )

        stream_started = ctx.time.perf_counter()
        generator = provider.complete(pruned_messages, stream=True)

        def sse_iterable():
            try:
                pre = {
                    "provider": info.name,
                    "model": info.model,
                    "memory_messages": len(stream_memory_messages),
                    "pruning": {
                        "original_tokens": stats.original_tokens,
                        "pruned_tokens": stats.pruned_tokens,
                        "removed_count": stats.removed_count,
                        "budget": stats.budget,
                        "reserve_output_tokens": stats.reserve_output_tokens,
                    },
                }
                yield (f"event: meta\ndata: {ctx.json.dumps(pre)}\n\n").encode()

                enc = None
                try:
                    import tiktoken as _tt

                    try:
                        from tiktoken import encoding_for_model

                        enc = encoding_for_model(info.model or "gpt-4o-mini")
                    except Exception:
                        enc = _tt.get_encoding("cl100k_base")
                except Exception:
                    enc = None

                cumulative_text = ""
                prev_token_count = 0
                prev_word_count = 0
                token_index = 0
                movement_commands_sent = False

                for chunk in generator:
                    if not chunk:
                        continue
                    next_text = cumulative_text + str(chunk)
                    if guardrails_enabled:
                        output_decision = ctx._ai_safety.validate_output(next_text)
                        if not output_decision.allowed:
                            ctx._AI_CAPABILITY_COUNTERS["safety_blocked_output"] += 1
                            ctx._record_ai_capability_event(
                                "chat_stream_output_blocked",
                                {
                                    "provider": info.name,
                                    "model": info.model,
                                    "risk_level": output_decision.risk_level,
                                    "reason": output_decision.reason,
                                    "flags": list(getattr(output_decision, "flags", ()) or ()),
                                },
                            )
                            chunk = ctx._build_guardrail_fallback_text()
                            payload = ctx.json.dumps({"delta": chunk})
                            yield (f"data: {payload}\n\n").encode()
                            yield b"data: [DONE]\n\n"
                            return

                    payload = ctx.json.dumps({"delta": chunk})
                    yield (f"data: {payload}\n\n").encode()
                    cumulative_text = next_text

                    if not movement_commands_sent and len(cumulative_text) > 20:
                        movement_data = ctx.parse_movement_commands(cumulative_text)
                        if movement_data.get("commands"):
                            yield (f"event: movement\ndata: {ctx.json.dumps(movement_data)}\n\n").encode()
                            movement_commands_sent = True

                    if enc is not None:
                        try:
                            token_ids = enc.encode(cumulative_text)
                            new_ids = token_ids[prev_token_count:]
                            if new_ids:
                                for token_id in new_ids:
                                    try:
                                        token_text = enc.decode([token_id])
                                    except Exception:
                                        token_text = ""
                                    yield (
                                        f"event: token\n"
                                        f"data: {ctx.json.dumps({'token_index': token_index, 'token': token_text, 'cumulative': cumulative_text})}\n\n"
                                    ).encode()
                                    token_index += 1
                                prev_token_count = len(token_ids)
                        except Exception:
                            enc = None

                    if enc is None:
                        words = list(ctx.re.finditer(r"\S+", cumulative_text))
                        if len(words) > prev_word_count:
                            for word in words[prev_word_count:]:
                                yield (
                                    f"event: token\n"
                                    f"data: {ctx.json.dumps({'token_index': token_index, 'token': word.group(0), 'cumulative': cumulative_text})}\n\n"
                                ).encode()
                                token_index += 1
                            prev_word_count = len(words)

                yield b"event: done\ndata: {}\n\n"
            except Exception as exc:
                yield (f"event: error\ndata: {ctx.json.dumps({'error': str(exc)})}\n\n").encode()
            finally:
                ctx._record_ai_latency(int((ctx.time.perf_counter() - stream_started) * 1000))
                yield b"data: [DONE]\n\n"

        return ctx._sse_response(sse_iterable(), status_code=200)
    except ValueError as exc:
        ctx.logging.error("chat/stream validation error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Validation error: {exc}"}),
            status_code=400,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("chat/stream error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": str(exc)}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def chat_stream_options(req, ctx):
    return ctx.func.HttpResponse("", status_code=200, headers=ctx.create_cors_response_headers())
