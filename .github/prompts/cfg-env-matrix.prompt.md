```prompt
---
agent: agent
description: Build environment configuration matrix across dev/test/stage/prod.
---
Task:
Document and validate environment-specific configuration values.
Requirements:
List mandatory keys, defaults, and allowed overrides.
Constraints:
Prevent production-only settings from leaking into lower envs.
Success Criteria:
Config differences are explicit, reviewed, and validated.
```
