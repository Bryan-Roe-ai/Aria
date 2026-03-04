```prompt
---
agent: agent
description: "Implement API response envelope with metadata wrapping"
---
# API Response Envelope
## Task
Implement consistent response envelope for all API responses.
## Requirements
1. Wrap responses in `{data, meta, errors}` envelope.
2. Include pagination metadata in `meta` field.
3. Include request timing in `meta` field.
4. Return `data` as null with `errors` array on failure.
5. Keep envelope consistent across all endpoints.
## Constraints
- Streaming endpoints may skip envelope. Health checks return raw. Everything else wrapped.
## Success Criteria
- All responses wrapped consistently. Metadata accurate. Error and success formats match.
```
