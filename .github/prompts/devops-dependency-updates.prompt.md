```prompt
---
agent: agent
description: "Implement dependency update automation with Dependabot/Renovate"
---
# Dependency Updates
## Task
Automate dependency updates with bot.
## Requirements
1. Configure automated PR creation for updates. 2. Group related updates.
3. Run tests on update PRs. 4. Auto-merge patch updates.
5. Review breaking changes manually.
## Constraints
- Auto-merge patches only. Group by ecosystem. Test before merge.
## Success Criteria
- Dependencies updated regularly. Tests pass before merge. Breaking changes reviewed.
```
