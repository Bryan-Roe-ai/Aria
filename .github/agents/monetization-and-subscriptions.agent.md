```chatagent
---
name: monetization-and-subscriptions
description: Subscription tiers, Stripe integration, referrals, and feature-gating for Aria's monetization layer.
---

# Monetization & Subscriptions Agent

## When to Use

- Adding or modifying subscription tiers, pricing, or feature gates.
- Stripe webhook handler changes (`shared/stripe_webhooks.py`).
- Referral system updates (`shared/referral_system.py`).
- Monetization HTML page fixes (`pricing.html`, `checkout.html`, `account.html`, etc.).
- Usage tracking or rate-limiting logic.

## Workflow

1. **Understand tiers** — Read `shared/subscription_manager.py` for `SubscriptionTier`, `Feature`, `TIER_FEATURES`, and `TIER_PRICING`.
2. **Locate integration points** — Stripe routes in `function_app.py`, frontend pages at repo root, and `shared/` modules.
3. **Implement** — Keep business logic in `shared/subscription_manager.py` and `shared/stripe_webhooks.py`; HTML pages consume via API calls.
4. **Sync pricing** — Ensure displayed prices and features in HTML match `TIER_PRICING` and `TIER_FEATURES`.
5. **Test** — Run `python scripts/test_runner.py --unit` and manually verify checkout flow against Stripe test mode.

## Guardrails

- Never expose Stripe secret keys client-side; use env vars (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`).
- Validate webhook signatures before processing events.
- Feature gates must fail-closed: deny access if tier lookup fails.
- Keep referral codes URL-safe and collision-resistant.
- Log subscription events for audit but never log full payment details.
```
