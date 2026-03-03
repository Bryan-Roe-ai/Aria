# QAI Quick Reference Card

## 🚀 Common Commands

### ⚡ Fast Validation (One Command)
```bash
# Full system health check (all infrastructure, configs, dependencies)
python scripts/fast_validate.py --fail-on-errors
```

### Development Server
```bash
func host start                                # Start Azure Functions locally
```

### Status Checks
```bash
# Full system status (includes telemetry, quantum, cosmos)
curl http://localhost:7071/api/ai/status | jq

# Specific sections
curl http://localhost:7071/api/ai/status | jq '.quantum'
curl http://localhost:7071/api/ai/status | jq '.telemetry'
curl http://localhost:7071/api/ai/status | jq '.cosmos'
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_validate_qiskit_env.py -v

# Run with coverage
pytest tests/ --cov=shared --cov=quantum/src
```

### Quantum Environment Management
```bash
# Validate current environment
python quantum/scripts/validate_qiskit_env.py

# Preview Qiskit 1.x upgrade
python quantum/scripts/upgrade_qiskit_to_1x.py --dry-run

# Apply upgrade (creates backup)
python quantum/scripts/upgrade_qiskit_to_1x.py --install

# Revert if needed
python quantum/scripts/upgrade_qiskit_to_1x.py --revert
```

### Training Orchestrators
```bash
# AutoTrain (LoRA fine-tuning)
python scripts/autotrain.py --dry-run --config config/training/autotrain.yaml
python scripts/autotrain.py --list --config config/training/autotrain.yaml
python scripts/autotrain.py --job phi35_mixed_chat --config config/training/autotrain.yaml

# Quantum AutoRun
python scripts/quantum_autorun.py --dry-run --config config/quantum/quantum_autorun.yaml
python scripts/quantum_autorun.py --list --config config/quantum/quantum_autorun.yaml
python scripts/quantum_autorun.py --job heart_quick --config config/quantum/quantum_autorun.yaml

# Evaluation AutoRun
python scripts/evaluation_autorun.py --dry-run --config config/evaluation/evaluation_autorun.yaml
python scripts/evaluation_autorun.py --list --config config/evaluation/evaluation_autorun.yaml
python scripts/evaluation_autorun.py --job eval_smoke_test --config config/evaluation/evaluation_autorun.yaml
```

### Chat Interaction
```bash
cd tools/talk-to-ai

# Local mode (FREE, offline)
python src/chat_cli.py --provider local --once "Hello"

# Azure OpenAI (requires env vars)
python src/chat_cli.py --provider azure

# OpenAI
python src/chat_cli.py --provider openai
```

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `local.settings.json` | Azure Functions local settings (API keys, connection strings) |
| `config/training/autotrain.yaml` | LoRA training job definitions |
| `config/quantum/quantum_autorun.yaml` | Quantum training job definitions |
| `config/evaluation/evaluation_autorun.yaml` | Model evaluation job definitions |
| `quantum/config/quantum_config.yaml` | Quantum backend settings |
| `lora/lora.yaml` | LoRA hyperparameters |

---

## 🌐 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ai/status` | GET | System health and diagnostics |
| `/api/chat` | POST | Chat completion (JSON response) |
| `/api/chat/stream` | POST | Streaming chat (SSE) |
| `/api/chat-web` | GET | Web chat interface |
| `/api/quantum/classify` | POST | Quantum classification |
| `/api/quantum/circuit` | POST | Quantum circuit visualization |
| `/api/quantum/info` | GET | Quantum capabilities |

---

## 🔑 Environment Variables

### Telemetry (Application Insights)
```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=...;IngestionEndpoint=..."
```

### Cosmos DB Persistence
```bash
export QAI_ENABLE_COSMOS="true"
export COSMOS_ENDPOINT="https://qai-cosmos.documents.azure.com:443/"
export COSMOS_KEY="your_primary_key_here"
export QAI_COSMOS_DATABASE="qai"
export QAI_COSMOS_CONTAINER="chat_sessions"
export QAI_COSMOS_PERSIST_STRATEGY="messages"  # or "sessions"
```

### Azure OpenAI
```bash
export AZURE_OPENAI_API_KEY="your_key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
export AZURE_OPENAI_API_VERSION="2024-08-01-preview"
```

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"  # optional
```

### Azure Quantum
```bash
export QAI_STATUS_CONNECT_AZURE_QUANTUM="true"  # Enable backend probing in status endpoint
```

---

## 📊 Status Endpoint JSON Structure

```json
{
  "active_provider": "azure|openai|local|lora",
  "model": "deployment-name or adapter-path",
  "telemetry": {
    "enabled": true|false
  },
  "cosmos": {
    "enabled": true|false,
    "initialized": true|false,
    "container_id": "chat_sessions"
  },
  "quantum": {
    "enabled": true|false,
    "qiskit": "0.46.0 or 1.x.x",
    "pennylane": "0.43.0",
    "conflict": true|false,
    "azure_quantum": {
      "workspace_connected": true|false,
      "backends": ["rigetti.sim.qvm", "ionq.simulator"]
    }
  },
  "lora": {
    "exists": true|false,
    "adapter_config_exists": true|false,
    "base_model": "microsoft/Phi-3.5-mini-instruct"
  }
}
```

---

## 🐛 Troubleshooting Quick Fixes

### Functions won't start
```bash
# Reinstall dependencies
python -m pip install -r requirements.txt

# Check port availability
lsof -i :7071  # On Linux/macOS
netstat -tuln | grep 7071  # Alternative
```

### Quantum conflict detected
```bash
# Option 1: Ignore (if quantum endpoints unused)
# Root venv conflict doesn't affect isolated quantum/venv

# Option 2: Upgrade root venv
cd quantum
python scripts/upgrade_qiskit_to_1x.py --install
```

### Tests not discovered
```bash
# Use full pytest path
python -m pytest tests/test_validate_qiskit_env.py -v
```

### Telemetry not appearing
```bash
# Verify connection string format
echo "$APPLICATIONINSIGHTS_CONNECTION_STRING"
# Should be: InstrumentationKey=...;IngestionEndpoint=https://...

# Check status endpoint
curl http://localhost:7071/api/ai/status | jq '.telemetry.enabled'
```

### Cosmos writes failing
```bash
# Check firewall rules in Azure Portal
# Ensure IP is allowlisted or "Allow from Azure Portal" enabled

# Verify credentials
curl http://localhost:7071/api/ai/status | jq '.cosmos.error'
```

---

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main project overview |
| [ENHANCEMENTS_SUMMARY.md](ENHANCEMENTS_SUMMARY.md) | Recent improvements (Nov 2025) |
| [TELEMETRY_COSMOS_ENABLEMENT.md](TELEMETRY_COSMOS_ENABLEMENT.md) | Observability setup guide |
| [QUANTUM_AUTORUN_README.md](QUANTUM_AUTORUN_README.md) | Quantum orchestrator usage |
| [AUTOTRAIN_README.md](AUTOTRAIN_README.md) | LoRA training orchestrator |
| [quantum/README.md](quantum/README.md) | Quantum AI project docs |