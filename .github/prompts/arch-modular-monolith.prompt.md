```prompt
---
agent: agent
description: "Implement modular monolith architecture"
---
# Modular Monolith
## Task
Structure a modular monolith with clear module boundaries.
## Requirements
1. Define modules with explicit public APIs. 2. Enforce module boundaries at compile time.
3. Each module owns its data. 4. Communication via module interfaces only.
5. Prepare for future extraction to services.
## Constraints
- No direct database access across modules. Public API only. Module-internal stays private.
## Success Criteria
- Modules have clear boundaries. No cross-module DB access. Extractable to services.
```
