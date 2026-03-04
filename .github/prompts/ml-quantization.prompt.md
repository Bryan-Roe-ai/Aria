```prompt
---
agent: agent
description: "Implement model quantization for deployment efficiency"
---
# Model Quantization
## Task
Quantize a model for efficient deployment.
## Requirements
1. Choose quantization method (GPTQ, AWQ, GGUF, bitsandbytes). 2. Evaluate accuracy impact of quantization.
3. Benchmark inference speed improvement. 4. Test quantized model quality.
5. Package for deployment.
## Constraints
- Accept < 2% accuracy loss for 4-bit. 8-bit for quality-sensitive tasks. Benchmark on target hardware.
## Success Criteria
- Model quantized. Accuracy loss acceptable. Speedup measured. Packaged for deploy.
```
