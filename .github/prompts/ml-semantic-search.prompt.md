```prompt
---
agent: agent
description: "Implement semantic search with re-ranking"
---
# Semantic Search
## Task
Build semantic search with two-stage retrieval and re-ranking.
## Requirements
1. First stage: fast retrieval with embeddings (top-100). 2. Second stage: re-rank with cross-encoder (top-10).
3. Implement hybrid search (keyword + semantic). 4. Handle query expansion.
5. Evaluate with MRR and NDCG.
## Constraints
- First stage must be < 100ms. Re-ranking < 500ms. Hybrid search combines scores.
## Success Criteria
- Two-stage retrieval improves relevance. Latency within targets. Metrics tracked.
```
