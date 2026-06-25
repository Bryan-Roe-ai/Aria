from __future__ import annotations


def unauthorized_response(req, ctx, scope: str):
    return ctx.func.HttpResponse(
        ctx.json.dumps({"status": "error", "error": "unauthorized", "scope": scope}),
        status_code=401,
        mimetype="application/json",
        headers=ctx.create_cors_response_headers(),
    )


def require_access(
    req,
    ctx,
    scope: str,
    *,
    extra_token_env_names: tuple[str, ...] = (),
    extra_header_names: tuple[str, ...] = (),
) -> object | None:
    normalized = scope.upper().replace("-", "_")
    protect_all = ctx._env_flag("QAI_PROTECT_RISKY_ROUTES", False)
    require_auth = ctx._env_flag(f"QAI_REQUIRE_AUTH_FOR_{normalized}", protect_all)

    token_required = None
    for env_name in (*extra_token_env_names, f"QAI_{normalized}_ACCESS_TOKEN", "QAI_ROUTE_ACCESS_TOKEN"):
        configured = ctx.os.getenv(env_name)
        if configured:
            token_required = configured
            break

    if not require_auth and not token_required:
        return None

    try:
        if ctx._request_has_platform_principal(req):
            return None
    except Exception:
        pass

    provided_token = ctx._extract_request_token(
        req,
        *extra_header_names,
        "X-QAI-ACCESS-TOKEN",
        "X-QAI-ROUTE-TOKEN",
        "Authorization",
    )
    if token_required and isinstance(provided_token, str) and ctx.hmac.compare_digest(provided_token, token_required):
        return None

    return unauthorized_response(req, ctx, scope)
