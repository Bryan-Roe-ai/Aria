```prompt
---
agent: agent
description: "Apply semantic pruning to models or conversation context"
---
# Semantic Pruning

## Task
Prune model layers, context windows, or training data using semantic relevance.

## Context
- Pruning script: `lora/scripts/semantic_pruning.py`
- Context pruning: `token_utils.prune_messages` (used by Functions chat routes)
- Chat memory: `shared/chat_memory.py` (cosine similarity for retrieval)

## Requirements
1. Identify the pruning target (model layers, conversation context, or dataset).
2. Define relevance criteria (semantic similarity, attention scores, recency).
3. Apply pruning while preserving critical information.
4. Validate that pruned output maintains acceptable quality.
5. Measure size reduction and quality impact.

## Constraints
- Never prune below minimum context requirements for the model.
- Preserve system prompts and recent messages in context pruning.
- Write pruned datasets to `data_out/`; keep originals intact.
- Document pruning parameters and quality impact.

## Success Criteria
- Size reduction meets the target (tokens, layers, or samples).
- Quality metrics remain within acceptable thresholds.
- Pruning is reproducible with documented parameters.
- No critical information lost in the pruning process.
```
