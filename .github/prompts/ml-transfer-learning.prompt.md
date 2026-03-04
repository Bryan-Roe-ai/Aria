```prompt
---
agent: agent
description: "Implement transfer learning from pre-trained models"
---
# Transfer Learning
## Task
Apply transfer learning from pre-trained models.
## Requirements
1. Select appropriate pre-trained model. 2. Freeze base layers, train classification head.
3. Gradually unfreeze layers for fine-tuning. 4. Use learning rate scheduling.
5. Evaluate against training from scratch.
## Constraints
- Start with frozen base. Unfreeze gradually. Use lower learning rate for pre-trained layers.
## Success Criteria
- Transfer learning outperforms from-scratch. Training efficient. Layer unfreezing helps.
```
