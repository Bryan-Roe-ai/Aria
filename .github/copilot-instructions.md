# QAI – Copilot Instructions

Essential knowledge for AI agents working in this hybrid quantum-AI/ML workspace. Focus: immediate productivity, safe execution, and cost awareness.

## Architecture Overview

**Three Independent Projects** (isolated venvs):
- `quantum-ai/` – Hybrid quantum-classical ML (PennyLane + Azure Quantum) + MCP Server
- `talk-to-ai/` – Multi-provider chat CLI (Azure OpenAI, OpenAI, LoRA, Local fallback)
- `AI/microsoft_phi-silica-3.6_v1/` – Phi-3.5 LoRA fine-tuning workspace

**Integration Layer**: Root `function_app.py` (Azure Functions) dynamically imports from all three via `sys.path` injection, enabling unified `/api/chat`, `/api/quantum/*`, and `/api/ai/status` endpoints.

**Shared Infrastructure**: `shared/` contains provider abstractions (`chat_providers.py`), SQL/Cosmos persistence (`db_logging.py`, `cosmos_client.py`, `sql_engine.py`), telemetry (`telemetry.py`), and memory retrieval (`chat_memory.py`).

## Orchestrator-Driven Workflow

**Critical Pattern**: All training/quantum jobs are YAML-driven orchestrators in `scripts/`:
- `autotrain.py` → `autotrain.yaml` (LoRA fine-tuning jobs)
- `quantum_autorun.py` → `quantum_autorun.yaml` (quantum ML training)
- `evaluation_autorun.py` → `evaluation_autorun.yaml` (model evaluation)

**Execution Protocol**:
1. **Always dry-run first**: `python .\scripts\autotrain.py --dry-run`
2. **Consume status.json**: Read `data_out/<orchestrator>/status.json` for job states (never parse stdout)
3. **Respect data immutability**: Read-only from `datasets/`, write-only to `data_out/`
4. **Config precedence**: YAML base < CLI flags < per-job YAML overrides

**Example Status JSON**:
```json
{
  "jobs": [{"name": "phi35_mixed_chat", "status": "validated", "dataset_samples": 1000}],
  "errors": [],
  "timestamp": "2025-11-24T10:30:00Z"
}
```

## Provider Auto-Detection

**Detection Order** (see `shared/chat_providers.py:detect_provider()`):
1. **Azure OpenAI**: Requires ALL 4 env vars (`AZURE_OPENAI_API_KEY`, `ENDPOINT`, `DEPLOYMENT`, `API_VERSION`)
2. **OpenAI**: Requires `OPENAI_API_KEY`
3. **LoRA**: Auto-detect if `adapter_model.safetensors` exists in adapter dir
4. **Local Echo**: Zero-dependency fallback (no API calls)

**Health Check**: `GET /api/ai/status` shows `active_provider`, missing env vars, LoRA readiness (`adapter_config.json` + `adapter_model.safetensors`), and SQL/Cosmos/Telemetry status.

**Adding Providers**: Subclass `BaseChatProvider.complete(messages, stream)`, add detection logic to `detect_provider()`, test with `chat_cli.py --provider <name>`.

## Quantum Computing Boundaries

**Two Modes**:
- **Training**: `quantum-ai/train_custom_dataset.py` (long-running, local simulator, epochs/batching)
- **MCP Server**: `quantum-ai/quantum_mcp_server.py` (8 tools, ≤10 qubits, ≤1k shots, 60s timeout, CircuitCache with LRU+TTL)

**Cost Gates**:
- Local simulators (qiskit_aer, pennylane default.qubit): FREE
- Azure simulators (ionq.simulator): FREE
- **Paid QPU** (ionq.qpu, quantinuum.*): ~$0.00003-$0.00015 per gate-shot
  - Safety: YAML jobs require `azure_confirm_cost: true`
  - Always test Bell state on simulator first: `quantum_autorun.py --job azure_ionq_simulator --dry-run`

**Auth**: `az login` + valid `quantum-ai/config/quantum_config.yaml` (subscription_id, resource_group, workspace).

## Testing Strategy

**Fast Unit Tests** (40 tests, ~0.5s):
```powershell
pytest tests/ -m "not slow and not azure"
# Or via orchestrator: python .\scripts\test_runner.py --unit
```

**Integration Tests** (30 tests, external services):
```powershell
pytest tests/ -m "integration"  # 29/30 passing
```

**VS Code Test Explorer**: Native UI integration (🧪 sidebar) with breakpoint debugging. See `VSCODE_TESTING_QUICKREF.md`.

**CI Pipeline**: `python .\scripts\ci_orchestrator.py --ci-pipeline` (5/10 critical steps passing: orchestrator validation + unit tests + artifact prep).

## Dataset & Training Conventions

**Dataset Structure** (immutable):
- `datasets/chat/<name>/train.json` + `test.json`
- Format: `[{"messages": [{"role": "user|assistant", "content": "..."}]}]`

**GPU Training**: `train_lora.py --device auto` (auto-detects cuda/directml/mps). Verify CUDA: `python -c "import torch; print(torch.cuda.is_available())"`. Install GPU build first: `pip install torch --index-url https://download.pytorch.org/whl/cu121`.

**Quick Smoke Test**:
```powershell
python .\AI\microsoft_phi-silica-3.6_v1\scripts\train_lora.py --dataset datasets/chat/mixed_chat --max-train-samples 64 --epochs 1
```

**LoRA Readiness Check**: Adapter ready when both exist:
- `data_out/lora_training/lora_adapter/adapter_config.json`
- `data_out/lora_training/lora_adapter/adapter_model.safetensors`

## Database & Observability (Optional)

**SQL Logging** (unified engine supports Azure SQL, PostgreSQL, MySQL, SQLite):
- Env: `QAI_DB_CONN` (ODBC connection string)
- Tables: `ChatConversations`, `QuantumTrainingRuns`, `LoRATrainingRuns`
- Graceful degradation: All `log_*_safe()` functions no-op if unavailable
- Health: `GET /api/ai/status` → `sql.pool.saturation_alert` (≥80% connections = warning)

**Cosmos DB Persistence** (feature-flagged):
- Enable: `QAI_ENABLE_COSMOS=true` + connection details in `shared/cosmos_client.py`
- Strategy: `QAI_COSMOS_PERSIST_STRATEGY=messages` (per-message) or `sessions` (full conversation)
- Graceful: Failures logged but don't block chat endpoint

**Telemetry** (Application Insights):
- Enable: `APPLICATIONINSIGHTS_CONNECTION_STRING` env var
- Spans: `/api/chat` annotated with provider, model, duration_ms, memory_injected, cosmos_persisted
- See `TELEMETRY_COSMOS_ENABLEMENT.md` for setup

## Key Commands Reference

```powershell
# Orchestrator dry-runs (validation only)
python .\scripts\autotrain.py --dry-run
python .\scripts\quantum_autorun.py --dry-run
python .\scripts\evaluation_autorun.py --dry-run

# Run specific job
python .\scripts\autotrain.py --job phi35_mixed_chat

# Azure Functions local dev
func host start  # Serves /api/chat, /api/ai/status, /api/quantum/*, /api/chat-web

# Chat CLI (multi-provider)
python .\talk-to-ai\src\chat_cli.py --provider azure --once "Test"
python .\talk-to-ai\src\chat_cli.py --provider lora --model data_out/lora_training/lora_adapter

# MCP Server (quantum tools for AI agents)
python .\quantum-ai\quantum_mcp_server.py

# Testing
pytest tests/ -m "not slow and not azure"  # Fast unit tests
python .\scripts\test_runner.py --all --coverage  # Full suite + HTML report
python .\scripts\ci_orchestrator.py --ci-pipeline  # Full CI validation

# Dataset validation
python .\scripts\validate_datasets.py --category chat

# Status checks
python .\scripts\master_orchestrator.py --status  # All orchestrators
curl http://localhost:7071/api/ai/status | jq  # Runtime health
```

## Common Pitfalls

1. **Azure OpenAI not detected**: Missing any of 4 required env vars (check `/api/ai/status` → `env.azure_openai`)
2. **LoRA fails to load**: Missing `adapter_model.safetensors` or base model mismatch in `adapter_config.json`
3. **Quantum job cost surprises**: Forgot `azure_confirm_cost: true` in YAML (safety gate prevents execution)
4. **Status JSON outdated**: Each orchestrator writes independent status files; use master_orchestrator for unified view
5. **Dataset not found**: Orchestrators run from repo root; relative paths in YAML assume `datasets/` prefix

## Safety & Secrets

- **No secrets in git**: Use `local.settings.json` (dev) or Azure App Settings (prod)
- **Dry-run everything first**: Prevents costly GPU/QPU runs with bad configs
- **Initial QPU shots ≤100**: Incremental cost validation before scaling
- **SQL connection pooling**: Monitor saturation alerts in `/api/ai/status` (threshold: 80% of max connections)

## References

- **AUTOTRAIN_README.md**: LoRA training orchestration details
- **QUANTUM_AUTORUN_README.md**: Quantum job configuration & Azure submission
- **TELEMETRY_COSMOS_ENABLEMENT.md**: Observability stack setup
- **VSCODE_TESTING_QUICKREF.md**: Test Explorer keyboard shortcuts
- **Root README.md**: Project overviews, quick starts, deployment guides

Last updated: 2025-11-25
