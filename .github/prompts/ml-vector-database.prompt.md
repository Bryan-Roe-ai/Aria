```prompt
---
agent: agent
description: "Implement vector database for similarity search"
---
# Vector Database
## Task
Set up and optimize a vector database for similarity search.
## Requirements
1. Choose vector DB (Chroma, Pinecone, Weaviate, FAISS). 2. Index embeddings with metadata.
3. Implement efficient search (ANN algorithms). 4. Handle index updates and deletions.
5. Optimize recall vs latency tradeoff.
## Constraints
- Choose index type based on dataset size. HNSW for < 10M vectors. Consider hosted vs self-hosted.
## Success Criteria
- Vector search fast and accurate. Index manageable. Recall/latency balanced.
```
