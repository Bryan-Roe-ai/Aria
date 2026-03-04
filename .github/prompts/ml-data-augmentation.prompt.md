```prompt
---
agent: agent
description: "Implement data augmentation for training set expansion"
---
# Data Augmentation
## Task
Implement data augmentation to expand training data.
## Requirements
1. Apply task-appropriate augmentations (text: paraphrase, back-translate; image: flip, rotate, crop).
2. Maintain label correctness after augmentation. 3. Control augmentation probability per sample.
4. Implement augmentation pipeline. 5. Validate augmented data quality.
## Constraints
- Augment only training data. Validate labels. Don't over-augment (quality > quantity).
## Success Criteria
- Training set expanded meaningfully. Labels correct. Model performance improved.
```
