```prompt
---
agent: agent
description: "Implement API search with filtering, sorting, and full-text"
---
# API Search
## Task
Implement search endpoints with filtering and sorting.
## Requirements
1. Support field-level filtering (`?status=active&type=admin`).
2. Support sorting (`?sort=created_at&order=desc`).
3. Support full-text search (`?q=search+term`).
4. Combine filters with AND logic.
5. Return result count and pagination metadata.
## Constraints
- Sanitize search inputs. Index searchable fields. Limit result set size.
## Success Criteria
- Filtering, sorting, and search work together. Results paginated. Inputs sanitized.
```
