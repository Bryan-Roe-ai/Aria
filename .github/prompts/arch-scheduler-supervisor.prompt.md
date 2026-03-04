```prompt
---
agent: agent
description: "Implement scheduler agent supervisor pattern"
---
# Scheduler-Agent-Supervisor
## Task
Implement scheduler-agent-supervisor for distributed task coordination.
## Requirements
1. Scheduler dispatches tasks to agents. 2. Agents execute and report status.
3. Supervisor monitors health and retries. 4. Handle agent failures.
5. Track task completion.
## Constraints
- Supervisor detects agent failure within 30s. Retry limit 3. Dead-letter for failed tasks.
## Success Criteria
- Tasks dispatched and completed. Failures retried. Supervisor catches hangs.
```
