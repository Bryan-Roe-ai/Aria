```prompt
---
agent: agent
description: "Debug chat memory retrieval, embedding generation, or context pruning issues"
---
# Chat Memory Debug

## Task
Diagnose and fix issues with chat memory: embedding generation, storage, or semantic retrieval.

## Context
- Memory module: `shared/chat_memory.py`
- Embedding providers: Azure OpenAI → OpenAI → local hash (dim=256)
- Storage: `[dbo].[ChatMessageEmbeddings]` table (float32 bytes)
- Retrieval: cosine similarity, top-k matches
- Context pruning: `token_utils.prune_messages`

## Requirements
1. Verify embedding provider availability (check env vars: `AZURE_OPENAI_API_KEY`, `OPENAI_API_KEY`).
2. Test `generate_embedding()` returns valid vectors.
3. Confirm embeddings are stored and retrievable from SQL.
4. Check cosine similarity returns relevant matches.
5. Validate context pruning keeps messages within token limits.

## Constraints
- Never log raw message content; use message IDs only.
- SQL queries must be parameterized.
- Local hash embeddings are not semantically meaningful; note this in results.
- Graceful fallback if database or API is unavailable.

## Success Criteria
- Embeddings generate, store, and retrieve correctly.
- Similarity search returns relevant prior context.
- Context pruning stays within configured token limits.
```
