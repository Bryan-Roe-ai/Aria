```prompt
---
agent: agent
description: "Configure or debug desktop and email notification channels"
---
# Notification Setup

## Task
Configure or troubleshoot notifications for training events and subscription alerts.

## Context
- Desktop: `scripts/notification_system.py` (Windows toast / macOS osascript / Linux notify-send)
- Email: `shared/email_notifications.py` (SMTP, templates)
- Config: `config/notification_config.yaml`
- Templates: `templates/emails/`

## Requirements
1. Identify the target platform and notification channel.
2. Configure thresholds and recipients in `config/notification_config.yaml`.
3. For new event types, extend `NotificationManager` or `EmailNotificationSystem`.
4. Add/update email templates in `templates/emails/` if needed.
5. Test notification delivery on the target platform.

## Constraints
- Handle missing backends gracefully (no crash if `win10toast` missing on Linux).
- Sanitize email HTML content; never include secrets or PII.
- Log notifications to `data_out/notifications/`.
- Keep notification frequency reasonable.

## Success Criteria
- Notifications fire correctly for the configured events.
- Missing backends degrade gracefully with console fallback.
- Notification log captures all sent events.
```
