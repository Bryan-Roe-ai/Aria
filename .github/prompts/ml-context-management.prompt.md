```prompt
---
agent: agent
description: "Implement token context management and pruning"
---
# Context Management
## Task
Implement token context management for LLM interactions.
## Requirements
1. Track token usage per conversation. 2. Implement context pruning when approaching limits.
3. Preserve system prompt and recent messages. 4. Summarize older context.
5. Follow Aria token_utils.prune_messages pattern.
## Constraints
- Never exceed model context window. Prioritize: system > recent > summary > old.
## Success Criteria
- Context stays within limits. Important context preserved. Summaries accurate.
```
