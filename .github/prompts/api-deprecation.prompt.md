```prompt
---
agent: agent
description: "Implement API deprecation strategy with sunset headers"
---
# API Deprecation
## Task
Implement API deprecation with sunset headers and migration guides.
## Requirements
1. Add `Deprecation: true` header to deprecated endpoints.
2. Add `Sunset: <date>` header with removal date.
3. Add `Link: <migration-url>; rel="successor-version"` header.
4. Log usage of deprecated endpoints for monitoring.
5. Return deprecation warning in response body.
## Constraints
- Minimum 6-month sunset period. Never remove without notice. Monitor adoption of new version.
## Success Criteria
- Deprecated endpoints marked with headers. Usage tracked. Migration path documented.
```
