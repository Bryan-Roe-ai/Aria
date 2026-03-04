```prompt
---
agent: agent
description: "Implement model fine-tuning with LoRA adapters"
---
# LoRA Fine-Tuning
## Task
Fine-tune a model using LoRA adapters.
## Requirements
1. Select base model and target modules. 2. Configure LoRA rank and alpha.
3. Prepare training data in instruction format. 4. Train with gradient accumulation.
5. Validate adapter with both files (adapter_config.json + adapter_model.safetensors).
## Constraints
- Follow Aria LoRA conventions. Datasets read-only, outputs to data_out/. Validate both adapter files.
## Success Criteria
- Adapter trained and validated. Both files present. Quality metrics improved over base.
```
