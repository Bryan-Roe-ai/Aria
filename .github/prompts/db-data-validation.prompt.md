```prompt
---
agent: agent
description: "Implement database data validation and constraints"
---
# Data Validation Constraints
## Task
Implement database-level data validation with constraints.
## Requirements
1. Define NOT NULL for required fields. 2. Add CHECK constraints for value ranges.
3. Implement UNIQUE constraints. 4. Add foreign key constraints.
5. Use triggers for complex validation.
## Constraints
- Validate at DB level as last defense. Application validates first. Constraints document rules.
## Success Criteria
- Invalid data rejected at DB level. Constraints document business rules. FK integrity enforced.
```
