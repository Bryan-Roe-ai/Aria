```prompt
---
agent: agent
description: "Optimize GPU memory usage and training throughput"
---
# GPU Optimization

## Task
Optimize GPU memory usage and training throughput for LoRA or quantum workloads.

## Context
- GPU optimizer: `lora/scripts/gpu_optimizer.py`
- VRAM calculator: `scripts/vram_calculator.py`
- GPU monitor: `dashboard/gpu_monitor.py`
- DeepSpeed config: `lora/scripts/deepspeed_zero3.json`
- Resource monitor: `scripts/resource_monitor.py`

## Requirements
1. Profile current GPU utilization with `gpu_monitor.py` or `nvidia-smi`.
2. Calculate memory requirements with `scripts/vram_calculator.py`.
3. Optimize batch size, gradient accumulation, and precision (fp16/bf16).
4. Enable gradient checkpointing or CPU offload if VRAM-constrained.
5. Re-benchmark to confirm improvement.

## Constraints
- Handle missing `nvidia-smi` gracefully (not all hosts have GPUs).
- Never exceed physical VRAM; leave headroom for OS overhead.
- Document optimization settings and measured impact.
- Test optimizations on a small batch before full training.

## Success Criteria
- Training runs without OOM errors on target hardware.
- GPU utilization is 80%+ (not wasting compute).
- Throughput (samples/sec) improved or maintained.
- Settings documented for reproducibility.
```
