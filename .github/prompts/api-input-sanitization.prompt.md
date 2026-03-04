```prompt
---
agent: agent
description: "Implement API input sanitization against injection attacks"
---
# API Input Sanitization
## Task
Implement input sanitization for injection prevention.
## Requirements
1. Sanitize HTML/script tags from text inputs. 2. Parameterize all SQL queries (never concatenate).
3. Validate JSON structure before parsing. 4. Sanitize file paths against traversal.
5. Encode output for the target context (HTML/URL/SQL).
## Constraints
- Sanitize on input, encode on output. Never trust client data. Use established libraries.
## Success Criteria
- Injection attacks blocked. SQL parameterized. Path traversal prevented. XSS encoded.
```
