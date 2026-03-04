```prompt
---
agent: agent
description: "Implement table-driven tests for comprehensive input coverage"
---
# Table-Driven Tests
## Task
Implement table-driven tests for systematic input coverage.
## Requirements
1. Define test cases as a table (list of dicts/tuples).
2. Include input, expected output, and description per case.
3. Use pytest.mark.parametrize to drive the table.
4. Cover normal, edge, and error cases in the table.
5. Make the table easy to extend with new cases.
## Constraints
- Table entries must be independent. Keep table readable.
## Success Criteria
- All input combinations are covered systematically. Adding cases is trivial.
```
