```prompt
---
agent: agent
description: "Implement environment variable management with validation and defaults"
---
# Environment Variables

## Task
Implement structured environment variable management with validation.

## Requirements
1. Define required and optional env vars with types and defaults.
2. Validate all required vars are present at startup.
3. Coerce string values to appropriate types (int, bool, list).
4. Provide a settings class/dict for centralized access.
5. Support `.env` file loading for local development.

## Constraints
- Never hardcode secrets; always use env vars.
- Fail fast on missing required vars with clear error messages.
- Document all env vars in a reference file.

## Success Criteria
- All env vars are validated at startup.
- Missing required vars cause immediate, clear failure.
- Settings are centralized and typed.
```
