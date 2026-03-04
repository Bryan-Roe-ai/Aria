```prompt
---
agent: agent
description: "Implement database schema versioning and compatibility"
---
# Schema Versioning
## Task
Implement database schema versioning for compatibility.
## Requirements
1. Version schema with migration numbers. 2. Support forward-only and rollback migrations.
3. Validate schema version on app startup. 4. Handle schema drift detection.
5. Document breaking changes.
## Constraints
- App asserts compatible schema version on startup. Never skip versions. Document breaking.
## Success Criteria
- Schema versioned. App validates compatibility. Drift detected. Breaking changes documented.
```
