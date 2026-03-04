```prompt
---
agent: agent
description: "Implement the repository pattern for data access abstraction"
---
# Repository Pattern

## Task
Implement the repository pattern to abstract data access.

## Requirements
1. Define a repository interface (Protocol) with CRUD methods.
2. Implement concrete repositories for SQL, Cosmos, in-memory.
3. Use the Unit of Work pattern for transaction management.
4. Support filtering, pagination, and sorting in queries.
5. Keep domain logic out of repository implementations.

## Constraints
- Repository methods should return domain objects, not raw data.
- Use parameterized queries in SQL implementations.
- In-memory implementation is for testing only.

## Success Criteria
- Data access is abstracted behind a clean interface.
- Switching storage backends requires no domain code changes.
- Queries are efficient and parameterized.
```
