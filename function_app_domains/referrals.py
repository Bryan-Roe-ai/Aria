from __future__ import annotations

from function_app_domains.access import require_access


def referral_code(req, ctx):
    unauthorized = require_access(req, ctx, "referrals")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Referral code endpoint invoked")
    try:
        from shared.referral_system import get_referral_system

        if req.method == "GET":
            user_id = req.params.get("user_id", "demo_user")
        else:
            user_id = ctx.json.loads(req.get_body().decode("utf-8")).get("user_id", "demo_user")

        referral_system = get_referral_system()
        code = referral_system.get_referral_code(user_id) or referral_system.generate_referral_code(user_id)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"referral_code": code, "user_id": user_id}),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Referral code error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to get referral code: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def referral_stats(req, ctx):
    unauthorized = require_access(req, ctx, "referrals")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Referral stats endpoint invoked")
    try:
        from shared.referral_system import get_referral_system

        stats = get_referral_system().get_referral_stats(req.params.get("user_id", "demo_user"))
        return ctx.func.HttpResponse(
            ctx.json.dumps(stats),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Referral stats error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to get referral stats: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def record_referral(req, ctx):
    unauthorized = require_access(req, ctx, "referrals")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Record referral endpoint invoked")
    try:
        from shared.referral_system import get_referral_system

        body = ctx.json.loads(req.get_body().decode("utf-8"))
        referrer_code = body.get("referrer_code")
        new_user_id = body.get("new_user_id")
        tier = body.get("tier")
        subscription_value = body.get("subscription_value")
        if not all([referrer_code, new_user_id, tier, subscription_value]):
            return ctx.func.HttpResponse(
                ctx.json.dumps({"error": "Missing required fields"}),
                status_code=400,
                mimetype="application/json",
                headers=ctx.create_cors_response_headers(),
            )

        result = get_referral_system().record_referral(
            referrer_code=referrer_code,
            new_user_id=new_user_id,
            tier=tier,
            subscription_value=subscription_value,
        )
        return ctx.func.HttpResponse(
            ctx.json.dumps(result),
            status_code=200 if result.get("success") else 400,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Record referral error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to record referral: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def referral_leaderboard(req, ctx):
    unauthorized = require_access(req, ctx, "referrals")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Referral leaderboard endpoint invoked")
    try:
        from shared.referral_system import get_referral_system

        leaderboard = get_referral_system().get_leaderboard(int(req.params.get("limit", "10")))
        return ctx.func.HttpResponse(
            ctx.json.dumps({"leaderboard": leaderboard}),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Referral leaderboard error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to get leaderboard: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
