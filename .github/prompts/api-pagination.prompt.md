```prompt
---
agent: agent
description: "Implement API pagination with cursor-based and offset styles"
---
# API Pagination
## Task
Implement pagination for list endpoints.
## Requirements
1. Support offset-based (`?page=1&limit=20`) pagination.
2. Support cursor-based (`?cursor=abc&limit=20`) pagination.
3. Return total count, next/prev links in response.
4. Handle edge cases (empty pages, last page, invalid cursor).
5. Set maximum page size limit.
## Constraints
- Default page size 20, max 100. Cursor-based for large datasets. Include metadata.
## Success Criteria
- Both styles work correctly. Edge cases handled. Navigation links accurate.
```
