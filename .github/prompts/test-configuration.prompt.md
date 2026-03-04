```prompt
---
agent: agent
description: "Test configuration loading and environment variable resolution"
---
# Configuration Tests
## Task
Write tests for configuration loading and environment variables.
## Requirements
1. Test YAML/JSON config file loading.
2. Test config precedence: base < CLI < per-job < env vars.
3. Test missing required config raises errors.
4. Test default values for optional config.
5. Use `monkeypatch` to set/unset env vars in tests.
## Constraints
- Follow Aria config precedence pattern. Never modify real env in tests.
## Success Criteria
- Config loading validated. Precedence order correct. Missing values raise errors.
```
