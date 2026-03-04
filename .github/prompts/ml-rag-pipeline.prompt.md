```prompt
---
agent: agent
description: "Implement RAG (Retrieval-Augmented Generation) pipeline"
---
# RAG Pipeline
## Task
Build a Retrieval-Augmented Generation pipeline.
## Requirements
1. Index documents with embeddings in vector store. 2. Implement semantic search for relevant context.
3. Construct prompt with retrieved context. 4. Generate response grounded in retrieved documents.
5. Implement citation and source attribution.
## Constraints
- Chunk documents appropriately (512-1024 tokens). Retrieve top-k (3-5). Include source metadata.
## Success Criteria
- Context retrieval relevant. Responses grounded in sources. Citations accurate.
```
