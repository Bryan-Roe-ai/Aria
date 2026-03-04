```prompt
---
agent: agent
description: "Implement secure environment variable handling"
---
# Secure Environment Variables
## Task
Handle environment variables securely.
## Requirements
1. Validate required env vars on startup. 2. Never log env var values.
3. Use .env files only for local development. 4. Document required env vars with descriptions.
5. Fail fast on missing critical env vars.
## Constraints
- Follow Aria convention: env vars or local.settings.json. Never commit .env files.
## Success Criteria
- Required vars validated on startup. No values logged. Documentation complete.
```
