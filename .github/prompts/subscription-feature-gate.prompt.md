```prompt
---
agent: agent
description: "Add, modify, or validate subscription tiers and feature gates"
---
# Subscription Feature Gate

## Task
Implement or update a subscription tier, feature gate, or pricing change.

## Context
- Tier definitions: `shared/subscription_manager.py` (`SubscriptionTier`, `Feature`, `TIER_FEATURES`, `TIER_PRICING`)
- Stripe hooks: `shared/stripe_webhooks.py`
- Referrals: `shared/referral_system.py`
- Frontend pages: `pricing.html`, `checkout.html`, `account.html`, `my-subscription.html`

## Requirements
1. Update `shared/subscription_manager.py` with new tiers/features/pricing.
2. Ensure feature gates fail-closed (deny access if tier lookup fails).
3. Sync displayed pricing in HTML pages with `TIER_PRICING`.
4. If touching Stripe, validate webhook signature handling.
5. Update relevant tests.

## Constraints
- No Stripe secret keys in client-side code.
- Referral codes must be URL-safe.
- Log subscription events but never log full payment details.

## Success Criteria
- New tier/feature is correctly gated and priced.
- HTML pages reflect accurate pricing.
- Unit tests pass for subscription logic.
```
