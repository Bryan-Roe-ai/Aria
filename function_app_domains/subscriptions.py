from __future__ import annotations

from function_app_domains.access import require_access


def subscription_pricing(req, ctx):
    ctx.logging.info("Pricing endpoint invoked")
    try:
        from shared.subscription_manager import TIER_FEATURES, TIER_LIMITS, TIER_PRICING, SubscriptionTier

        pricing_info = {"tiers": {}}
        for tier in SubscriptionTier:
            pricing_info["tiers"][tier.value] = {
                "name": tier.name,
                "price": TIER_PRICING[tier],
                "currency": "USD",
                "billing_period": "monthly",
                "features": {feature.value: enabled for feature, enabled in TIER_FEATURES[tier].items()},
                "limits": TIER_LIMITS[tier],
            }

        return ctx.func.HttpResponse(
            ctx.json.dumps(pricing_info),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Pricing endpoint error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to get pricing: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def subscription_status(req, ctx):
    unauthorized = require_access(req, ctx, "subscriptions")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Subscription status endpoint invoked")
    try:
        if not ctx.subscription_manager_available:
            return ctx.func.HttpResponse(
                ctx.json.dumps({"error": "Subscription manager not available"}),
                status_code=503,
                mimetype="application/json",
                headers=ctx.create_cors_response_headers(),
            )

        user_id = req.params.get("user_id", "demo_user")
        manager = ctx.get_subscription_manager()
        subscription = manager.get_subscription(user_id)
        return ctx.func.HttpResponse(
            ctx.json.dumps(subscription.to_dict()),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Subscription status error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to get subscription status: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def subscription_upgrade(req, ctx):
    unauthorized = require_access(req, ctx, "subscriptions")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Subscription upgrade endpoint invoked")
    try:
        if not ctx.subscription_manager_available:
            return ctx.func.HttpResponse(
                ctx.json.dumps({"error": "Subscription manager not available"}),
                status_code=503,
                mimetype="application/json",
                headers=ctx.create_cors_response_headers(),
            )

        body = ctx.json.loads(req.get_body().decode("utf-8"))
        user_id = body.get("user_id", "demo_user")
        tier = ctx.SubscriptionTier(body.get("tier", "pro"))
        subscription = ctx.get_subscription_manager().upgrade_subscription(
            user_id=user_id,
            tier=tier,
            duration_days=body.get("duration_days", 30),
            payment_method=body.get("payment_method"),
            stripe_subscription_id=body.get("stripe_subscription_id"),
        )
        return ctx.func.HttpResponse(
            ctx.json.dumps({"success": True, "subscription": subscription.to_dict()}),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Subscription upgrade error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to upgrade subscription: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def subscription_revenue(req, ctx):
    unauthorized = require_access(req, ctx, "subscriptions")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Revenue stats endpoint invoked")
    try:
        if not ctx.subscription_manager_available:
            return ctx.func.HttpResponse(
                ctx.json.dumps({"error": "Subscription manager not available"}),
                status_code=503,
                mimetype="application/json",
                headers=ctx.create_cors_response_headers(),
            )

        stats = ctx.get_subscription_manager().get_revenue_stats()
        return ctx.func.HttpResponse(
            ctx.json.dumps(stats),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Revenue stats error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to get revenue stats: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def subscription_track_usage(req, ctx):
    unauthorized = require_access(req, ctx, "subscriptions")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Usage tracking endpoint invoked")
    try:
        if not ctx.subscription_manager_available:
            return ctx.func.HttpResponse(
                ctx.json.dumps({"error": "Subscription manager not available"}),
                status_code=503,
                mimetype="application/json",
                headers=ctx.create_cors_response_headers(),
            )

        body = ctx.json.loads(req.get_body().decode("utf-8"))
        user_id = body.get("user_id", "demo_user")
        resource = body.get("resource", "api_requests")
        amount = body.get("amount", 1)

        manager = ctx.get_subscription_manager()
        allowed = manager.track_usage(user_id, resource, amount)
        subscription = manager.get_subscription(user_id)

        return ctx.func.HttpResponse(
            ctx.json.dumps(
                {
                    "success": True,
                    "allowed": allowed,
                    "current_usage": subscription.usage,
                    "limits": subscription.to_dict()["limits"],
                }
            ),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Usage tracking error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to track usage: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def stripe_webhook(req, ctx):
    ctx.logging.info("Stripe webhook endpoint invoked")
    try:
        from shared.stripe_webhooks import get_webhook_handler

        result = get_webhook_handler().handle_webhook(
            req.get_body().decode("utf-8"),
            req.headers.get("Stripe-Signature", ""),
            ctx.os.environ.get("STRIPE_WEBHOOK_SECRET"),
        )
        status_code = 200 if result["status"] in ["success", "ignored"] else 500
        return ctx.func.HttpResponse(
            ctx.json.dumps(result),
            status_code=status_code,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Stripe webhook error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"status": "error", "message": str(exc)}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def test_notifications(req, ctx):
    unauthorized = require_access(req, ctx, "notifications")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Test notification endpoint invoked")
    try:
        from shared.email_notifications import get_email_system

        body = ctx.json.loads(req.get_body().decode("utf-8"))
        email = body.get("email", "test@example.com")
        notification_type = body.get("type", "usage_warning")
        email_system = get_email_system()

        if notification_type == "usage_warning":
            success = email_system.notify_usage_warning(
                user_email=email,
                resource="chat_messages",
                percentage=85.0,
                current=850,
                limit=1000,
            )
        elif notification_type == "payment_succeeded":
            success = email_system.notify_payment_succeeded(user_email=email, amount=49.00, invoice_id="inv_test123")
        elif notification_type == "subscription_activated":
            success = email_system.notify_subscription_activated(user_email=email, tier="Pro", price=49.00)
        else:
            return ctx.func.HttpResponse(
                ctx.json.dumps({"error": f"Unknown notification type: {notification_type}"}),
                status_code=400,
                mimetype="application/json",
                headers=ctx.create_cors_response_headers(),
            )

        return ctx.func.HttpResponse(
            ctx.json.dumps({"success": success, "message": f"Test notification sent to {email}", "type": notification_type}),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Test notification error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to send test notification: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )


def notifications_log(req, ctx):
    unauthorized = require_access(req, ctx, "notifications")
    if unauthorized is not None:
        return unauthorized

    ctx.logging.info("Notifications log endpoint invoked")
    try:
        from shared.email_notifications import get_email_system

        notifications = get_email_system().get_sent_emails(req.params.get("user_email"))
        return ctx.func.HttpResponse(
            ctx.json.dumps({"notifications": notifications, "count": len(notifications)}),
            status_code=200,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
    except Exception as exc:
        ctx.logging.error("Notifications log error: %s", exc)
        return ctx.func.HttpResponse(
            ctx.json.dumps({"error": f"Failed to get notifications log: {exc}"}),
            status_code=500,
            mimetype="application/json",
            headers=ctx.create_cors_response_headers(),
        )
