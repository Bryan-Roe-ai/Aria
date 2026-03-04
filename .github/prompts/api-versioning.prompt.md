```prompt
---
agent: agent
description: "Implement API versioning strategy for backward compatibility"
---
# API Versioning
## Task
Implement API versioning for backward compatibility.
## Requirements
1. Choose versioning strategy (URL path `/v1/`, header, query param).
2. Support multiple active versions simultaneously.
3. Implement version deprecation notices in response headers.
4. Document migration path between versions.
5. Test backward compatibility of existing clients.
## Constraints
- Prefer URL path versioning for simplicity. Never break existing clients.
## Success Criteria
- Multiple versions coexist. Deprecation communicated. Old clients unaffected.
```
