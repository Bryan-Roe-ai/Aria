```prompt
---
agent: agent
description: "Implement named entity recognition (NER) pipeline"
---
# Named Entity Recognition
## Task
Build a named entity recognition pipeline.
## Requirements
1. Select NER model (spaCy, Hugging Face, custom). 2. Define entity types.
3. Prepare annotated training data. 4. Train and evaluate with entity-level F1.
5. Handle overlapping and nested entities.
## Constraints
- Use BIO/IOB2 tagging scheme. Evaluate at entity level, not token level. Handle edge cases.
## Success Criteria
- NER model trained. Entity-level F1 meeting target. Edge cases handled.
```
