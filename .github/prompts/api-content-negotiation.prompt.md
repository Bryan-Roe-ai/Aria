```prompt
---
agent: agent
description: "Implement API content negotiation for multiple formats"
---
# API Content Negotiation
## Task
Implement content negotiation for multiple response formats.
## Requirements
1. Parse `Accept` header for client preference.
2. Support JSON (default), XML, and CSV responses.
3. Return 406 Not Acceptable for unsupported formats.
4. Set `Content-Type` header matching response format.
5. Support `?format=json` query parameter fallback.
## Constraints
- JSON is always default. Only implement formats actively needed. Negotiate via Accept header.
## Success Criteria
- Correct format returned per Accept header. 406 for unsupported. Content-Type matches.
```
