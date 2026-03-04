```prompt
---
agent: agent
description: "Implement pre-commit hooks for code quality"
---
# Pre-Commit Hooks
## Task
Set up pre-commit hooks for code quality.
## Requirements
1. Format code (black, prettier). 2. Lint code (ruff, eslint).
3. Check for secrets (detect-secrets). 4. Validate YAML/JSON.
5. Run type checks.
## Constraints
- Hooks must be fast (< 10s). Skip heavy tests. Focus on formatting and security.
## Success Criteria
- Code formatted on commit. Secrets detected. Lint errors caught. Type issues flagged.
```
