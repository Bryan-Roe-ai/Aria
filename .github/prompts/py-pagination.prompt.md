```prompt
---
agent: agent
description: "Implement pagination for large result sets with cursor and offset styles"
---
# Pagination
## Task
Implement pagination for large result sets.
## Requirements
1. Support both offset-based and cursor-based pagination.
2. Return consistent page metadata (total, page, page_size, next_cursor).
3. Optimize database queries with LIMIT/OFFSET or keyset pagination.
4. Handle edge cases (empty results, last page, invalid cursors).
5. Add pagination parameters to API endpoints.
## Constraints
- Cursor-based is preferred for large datasets (no offset performance penalty).
- Set a maximum page size to prevent abuse.
- Return stable results during pagination (ordering required).
## Success Criteria
- Large datasets are paginated efficiently.
- Page metadata is correct and complete.
- No duplicate or missing records across pages.
```
