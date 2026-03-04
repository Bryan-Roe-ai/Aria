```instructions
---
name: "Templates-Emails"
description: "Guidance for templates/emails/ notification email templates"
applyTo: "templates/emails/**"
---
# Email Templates

- `templates/emails/` contains HTML email templates for subscription and notification events.
- Templates are consumed by `shared/email_notifications.py`.
- Use inline CSS for email compatibility (no external stylesheets).
- Sanitize all dynamic content; never include raw user input without escaping.
- Keep templates responsive and tested across major email clients.
- Template variables should be clearly delimited (e.g., `{{ variable }}`).
- Never include secrets, API keys, or full payment details in templates.
- Include unsubscribe links where legally required.
- Test rendering with both light and dark mode email clients.
```
