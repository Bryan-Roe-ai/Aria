```prompt
---
agent: agent
description: "Implement API partial responses with field selection"
---
# API Partial Responses
## Task
Implement field selection for partial API responses.
## Requirements
1. Support `?fields=id,name,email` query parameter. 2. Return only requested fields in response.
3. Validate field names against schema. 4. Support nested field selection with dot notation.
5. Always include `id` field regardless of selection.
## Constraints
- Unknown fields return 400. Default to full response if no selection. Document available fields.
## Success Criteria
- Only selected fields returned. Nested selection works. Invalid fields rejected.
```
