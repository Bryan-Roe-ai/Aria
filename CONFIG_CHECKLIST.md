# ✅ Aria Environment Configuration — Quick Checklist

**Status:** May 16, 2026 — Environment configured and ready
**Python:** 3.14 (configured for main + all sub-projects)

---

## 📋 What Was Configured

✅ **Main Aria Workspace**

- Location: `/workspaces/Aria`
- Venv: `/workspaces/Aria/.venv`
- Status: Ready for pip install

✅ **Quantum ML Sub-Project**

- Location: `ai-projects/quantum-ml`
- Venv: Shares main `.venv`
- Key: `qiskit==1.3.0`, `azure-quantum[qiskit]`

✅ **Chat CLI Sub-Project**

- Location: `ai-projects/chat-cli`
- Venv: Shares main `.venv`
- Key: `openai>=1.58.0`

✅ **LoRA Training Sub-Project**

- Location: `AI/microsoft_phi-silica-3.6_v1`
- Venv: Shares main `.venv`
- Key: PyTorch training scripts

✅ **Provider Detection Chain**

- LMStudio → Azure OpenAI → OpenAI → LoRA → Local fallback
- Config: `local.settings.json` (all providers optional)

---

## 🚀 Next Steps (Copy & Paste Ready)

### 1️⃣ Install All Dependencies

```bash
cd /workspaces/Aria

# Main
pip install -r requirements.txt

# Optional: Dev tools (linting, testing)
pip install -r requirements-dev.txt

# Sub-projects
pip install -r ai-projects/quantum-ml/requirements.txt
pip install -r ai-projects/chat-cli/requirements.txt
pip install -r ai-projects/llm-maker/requirements.txt
pip install -r ai-projects/cooking-ai/requirements.txt
```

### 2️⃣ Quick Validation

```bash
# Fast validation (all checks pass? → good to go)
python scripts/fast_validate.py

# Critical deps check
python3 -c "
import sys
pkgs = ['torch', 'transformers', 'qiskit', 'azure-quantum', 'openai']
missing = [p for p in pkgs if __import__(p.replace('-', '_'), fromlist=['']) is None]
print('✓ All critical packages' if not missing else f'✗ Missing: {missing}')
sys.exit(0 if not missing else 1)
"
```

### 3️⃣ Configure Secrets (Optional)

If you have API keys, edit `local.settings.json`:

```json
{
    "Values": {
        "AZURE_OPENAI_API_KEY": "your-key",
        "AZURE_OPENAI_ENDPOINT": "your-endpoint",
        "OPENAI_API_KEY": "your-key",
        "LMSTUDIO_BASE_URL": "http://localhost:1234/v1"
    }
}
```

### 4️⃣ Start Azure Functions

```bash
func host start
```

### 5️⃣ Test API Endpoints (In another terminal)

```bash
# Health check
curl http://localhost:7071/api/ai/status | python3 -m json.tool

# Provider probe
curl -X POST http://localhost:7071/api/ai/provider-probe \
  -H 'Content-Type: application/json' \
  -d '{"provider":"auto"}' | python3 -m json.tool

# List routes
curl http://localhost:7071/api/ai/routes | python3 -m json.tool
```

---

## 📦 Dependency Summary

| Category          | Key Package                   | Min Version |
| ----------------- | ----------------------------- | ----------- |
| **AI/Chat**       | `openai`                      | 1.58.0      |
| **Quantum**       | `qiskit`                      | 1.3.0       |
| **Quantum ML**    | `qiskit-machine-learning`     | 0.8.2       |
| **Azure Quantum** | `azure-quantum`               | 1.0.0       |
| **Deep Learning** | `torch`                       | 2.8.0       |
| **Transformers**  | `transformers`                | Latest      |
| **Fine-tuning**   | `peft`                        | Latest      |
| **Functions**     | `azure-functions`             | Latest      |
| **Database**      | `sqlalchemy`                  | 2.0.36      |
| **Cosmos**        | `azure-cosmos`                | 4.7.0       |
| **Telemetry**     | `azure-monitor-opentelemetry` | 1.0.0       |

---

## 🔌 Provider Detection (Auto-Detected Order)

```
1. LMStudio?     → LMSTUDIO_BASE_URL set?
2. Azure OpenAI? → All 4 vars set?
3. OpenAI?       → OPENAI_API_KEY set?
4. LoRA?         → Explicit --provider lora?
5. Local?        → Zero-config fallback ✓
```

**To force a provider:**

```bash
# CLI
python ai-projects/chat-cli/src/chat_cli.py --provider openai --once "Hello"

# API (via function_app.py)
curl -X POST http://localhost:7071/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"provider":"azure-openai","message":"Hello"}'
```

---

## ✅ Validation Commands

### Test Each Component

```bash
# Chat CLI (local, no setup needed)
python ai-projects/chat-cli/src/chat_cli.py --provider local --once "Test"

# Quantum simulation
python -c "from qiskit import QuantumCircuit; print('✓ qiskit')"

# Torch GPU (if available)
python -c "import torch; print(f'✓ torch (GPU: {torch.cuda.is_available()})')"

# Azure Functions
func host start  # Then: curl http://localhost:7071/api/ai/status
```

### Run Test Suite

```bash
# Unit tests only
pytest tests/ -m "not slow and not azure" -v

# With coverage
pytest tests/ -m "not slow and not azure" --cov

# Using test runner
python scripts/test_runner.py --unit
```

---

## 🛠️ Optional: Isolated Venvs

If you need separate venvs per project (e.g., conflicting deps), create them:

```bash
# Quantum ML isolated
cd ai-projects/quantum-ml
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Chat CLI isolated
cd ai-projects/chat-cli
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Update VS Code settings → python.defaultInterpreterPath
```

---

## 📚 Full Documentation

See `ENVIRONMENT_SETUP.md` for:

- ✓ Detailed dependency lists
- ✓ Provider configuration examples
- ✓ API endpoint docs
- ✓ Troubleshooting
- ✓ Advanced setup (SQL, Cosmos, Telemetry)

---

## 🆘 Quick Troubleshooting

| Problem                       | Fix                                      |
| ----------------------------- | ---------------------------------------- |
| `ModuleNotFoundError: torch`  | `pip install torch>=2.8.0`               |
| `ModuleNotFoundError: qiskit` | `pip install qiskit==1.3.0`              |
| `ModuleNotFoundError: openai` | `pip install openai>=1.58.0`             |
| Provider returns "local"      | Check `/api/ai/status` for env vars      |
| `/api/chat` returns 500       | Run `/api/ai/provider-probe` to diagnose |
| Functions fail to start       | `pip install azure-functions`            |

---

## 📝 Files Modified

✅ **Created:** `ENVIRONMENT_SETUP.md` (full reference guide)
✅ **Referenced:** `local.settings.json.example` (provider config template)
✅ **Noted:** `requirements.txt` (main + all sub-projects)
✅ **Ready:** `pyproject.toml` (project metadata)

---

## ✨ You're Ready To:

- ✅ Install all Python dependencies
- ✅ Start Azure Functions runtime
- ✅ Test chat with multiple providers
- ✅ Run quantum simulations
- ✅ Fine-tune LoRA models
- ✅ Execute integrated tests

**Next:** Run the **4 quick install commands** above! 🎉

---

Generated: May 16, 2026
Configuration: ✅ Complete
Ready: ✅ Yes
