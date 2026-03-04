```chatagent
---
name: notification-system
description: Cross-platform desktop and email notification configuration for training events and subscription alerts.
---

# Notification System Agent

## When to Use

- Configuring desktop notifications (`scripts/notification_system.py`).
- Setting up email notifications (`shared/email_notifications.py`).
- Editing notification config (`config/notification_config.yaml`).
- Adding new notification event types or templates.

## Workflow

1. **Choose channel** — Desktop (Windows toast / macOS osascript / Linux notify-send) or email.
2. **Configure** — Edit `config/notification_config.yaml` for thresholds and recipients.
3. **Implement** — For new event types, add to `NotificationManager` or `EmailNotificationSystem`.
4. **Template** — Email templates use `templates/emails/`; keep them HTML-safe and PII-free.
5. **Test** — Verify notifications fire correctly on the target platform.

## Guardrails

- Handle missing notification backends gracefully (e.g., no `win10toast` on Linux).
- Never include secrets or full payment details in notification content.
- Email: sanitize HTML; use pre-compiled regex patterns for stripping.
- Write notification logs to `data_out/notifications/`.
- Keep notification frequency reasonable; avoid spamming users.
```
