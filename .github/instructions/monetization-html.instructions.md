```instructions
---
name: "Monetization-HTML"
description: "Guidance for root-level monetization and subscription HTML pages"
applyTo: "{pricing,checkout,account,my-subscription,subscription-success,referrals,monetization-index}.html"
---
# Monetization Pages – HTML

- Root HTML files (`pricing.html`, `checkout.html`, `account.html`, etc.) are the customer-facing monetization surfaces.
- Subscription tiers are defined in `shared/subscription_manager.py`; keep displayed pricing and features in sync.
- Stripe integration: checkout flow hits `/api/stripe/webhook`; never expose Stripe secret keys client-side.
- Referral system: `referrals.html` ties to `shared/referral_system.py`; display referral codes server-rendered or via API.
- All pages must be accessible (ARIA labels, keyboard nav, contrast ratios).
- Keep styles consistent across monetization pages; prefer shared CSS classes.
- Link back to `/api/ai/status` or subscription API endpoints for dynamic feature-gate display.
- Do not hardcode prices; fetch from API or use server-side template variables.
```
