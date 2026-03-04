```prompt
---
agent: agent
description: "Serve a trained model for inference via the model server"
---
# Model Serving

## Task
Deploy a trained LoRA adapter or model for inference using the model server.

## Context
- Model server: `lora/scripts/model_server.py`
- Model exporter: `lora/scripts/model_exporter.py`
- Deployed models: `deployed_models/`
- Model registry: `deployed_models/model_registry.json`

## Requirements
1. Export the trained model if conversion is needed (`model_exporter.py`).
2. Validate adapter readiness (both `adapter_config.json` and `adapter_model.safetensors`).
3. Configure the server (host, port, model path, max concurrent requests).
4. Start the server and verify health endpoint responds.
5. Run inference tests against the served model.

## Constraints
- Bind to localhost by default; require explicit flag for network exposure.
- Do not load untrusted models without validation.
- Set request timeouts and concurrency limits.
- Log inference requests for monitoring but omit PII.

## Success Criteria
- Server starts and health endpoint returns OK.
- Inference requests return valid responses.
- Throughput and latency meet acceptable benchmarks.
- Server handles concurrent requests without crashes.
```
