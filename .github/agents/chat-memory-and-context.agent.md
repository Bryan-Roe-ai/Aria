```chatagent
---
name: chat-memory-and-context
description: Semantic chat memory, embedding generation, context pruning, and conversation history management.
---

# Chat Memory & Context Agent

## When to Use

- Modifying `shared/chat_memory.py` (embedding generation, storage, similarity search).
- Tuning context pruning in `token_utils.prune_messages`.
- Debugging chat context window issues or stale memory retrieval.
- Configuring embedding providers (Azure OpenAI → OpenAI → local hash fallback).

## Workflow

1. **Understand pipeline** — Messages → `generate_embedding(text)` → `store_embedding()` → `fetch_similar_messages()` for retrieval.
2. **Check providers** — Azure OpenAI embeddings first, then OpenAI, then local hash. Verify env vars.
3. **Inspect storage** — Embeddings stored as float32 bytes in `[dbo].[ChatMessageEmbeddings]`.
4. **Tune retrieval** — Adjust `top_k`, similarity thresholds, or session scoping.
5. **Test** — Validate with unit tests; check that pruning keeps context within token limits.

## Guardrails

- Embedding provider fallback must be graceful; never crash on missing API keys.
- Local hash embedding is a last resort — fixed dim=256, not semantically meaningful.
- Never log raw message content in telemetry; log only metadata.
- SQL queries for embeddings must be parameterized.
- Keep embedding storage schema in sync with `database/Tables/ChatMessageEmbeddings.sql`.
```
