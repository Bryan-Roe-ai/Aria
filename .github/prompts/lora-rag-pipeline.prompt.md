```prompt
---
agent: agent
description: "Set up a RAG pipeline with LoRA adapters for retrieval-augmented generation"
---
# LoRA RAG Pipeline

## Task
Configure and run a Retrieval-Augmented Generation pipeline using LoRA adapters.

## Context
- RAG pipeline: `lora/scripts/rag_pipeline.py`
- Dataset preparation: `lora/scripts/prepare_dataset.py`
- Model server: `lora/scripts/model_server.py`
- LoRA training: `lora/scripts/train_lora.py`

## Requirements
1. Prepare a document corpus for retrieval.
2. Configure the vector store and embedding model.
3. Set up the LoRA adapter for generation.
4. Wire retrieval results into the generation context.
5. Test end-to-end: query → retrieve → augment → generate.

## Constraints
- Ensure vector store is initialized before querying.
- Keep retrieval-augmented context within token limits.
- Write outputs to `data_out/`; datasets are read-only.
- Validate adapter readiness (both adapter files present).

## Success Criteria
- RAG pipeline retrieves relevant documents for test queries.
- Generation quality improves over non-RAG baseline.
- Pipeline runs within memory/VRAM constraints.
- End-to-end latency is acceptable for the use case.
```
