```prompt
---
agent: agent
description: "Write golden file tests for complex output verification"
---
# Golden File Tests
## Task
Implement golden file tests for complex output verification.
## Requirements
1. Generate output and save as golden file.
2. Compare current output against golden file.
3. Support updating goldens with `--update-goldens` flag.
4. Normalize non-deterministic values before comparison.
5. Store golden files alongside tests in version control.
## Constraints
- Golden file updates require manual review. Normalize timestamps, IDs, and paths.
## Success Criteria
- Output changes detected automatically. Golden updates are reviewed before commit.
```
