from __future__ import annotations

from function_app_domains.access import require_access


def aria_state_proxy(req, ctx):
    return ctx._proxy_aria_request(req, "state")


def aria_execute_proxy(req, ctx):
    if req.method.upper() == "OPTIONS":
        return ctx.func.HttpResponse("", status_code=200, headers=ctx.create_cors_response_headers())
    unauthorized = require_access(req, ctx, "aria")
    if unauthorized is not None:
        return unauthorized
    return ctx._proxy_aria_request(req, "execute")


def aria_command_proxy(req, ctx):
    if req.method.upper() == "OPTIONS":
        return ctx.func.HttpResponse("", status_code=200, headers=ctx.create_cors_response_headers())
    unauthorized = require_access(req, ctx, "aria")
    if unauthorized is not None:
        return unauthorized
    return ctx._proxy_aria_request(req, "command")
