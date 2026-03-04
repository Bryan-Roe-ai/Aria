```prompt
---
agent: agent
description: "Implement API webhook delivery and retry mechanism"
---
# API Webhooks
## Task
Implement webhook delivery with retry and verification.
## Requirements
1. Register webhook URL with event types.
2. Send POST with signed payload (HMAC-SHA256).
3. Retry failed deliveries with exponential backoff.
4. Log delivery status and response codes.
5. Support webhook secret rotation.
## Constraints
- Max 5 retries. Include `X-Webhook-Signature` header. Timeout 30s per delivery.
## Success Criteria
- Webhooks delivered with signature. Retries work. Failed deliveries logged.
```
