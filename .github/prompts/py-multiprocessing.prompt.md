```prompt
---
agent: agent
description: "Implement multiprocessing for CPU-bound parallel workloads"
---
# Multiprocessing

## Task
Implement multiprocessing for CPU-bound parallel workloads.

## Requirements
1. Use `multiprocessing.Pool` or `ProcessPoolExecutor` for parallel map.
2. Handle shared state with `Manager` or `Queue`.
3. Implement proper process cleanup and error handling.
4. Use `mp.cpu_count()` for sensible defaults.
5. Add progress tracking for long-running parallel tasks.

## Constraints
- Ensure all data passed between processes is picklable.
- Handle keyboard interrupts gracefully in worker processes.
- Set timeouts on pool operations to prevent hangs.

## Success Criteria
- CPU-bound work parallelized across available cores.
- Process cleanup happens even on errors.
- Speedup is measurable over single-process baseline.
```
