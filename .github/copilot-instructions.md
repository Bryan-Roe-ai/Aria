# QAI Workspace – AI Agent Guide

**Three independent AI/ML projects** in one monorepo, each with isolated virtual environments, configs, and workflows:
- **`quantum-ai/`** – Hybrid quantum-classical ML (Azure Quantum + Qiskit/PennyLane) + MCP server
- **`talk-to-ai/`** – Multi-provider CLI chat (OpenAI/Azure/Local fallback)
- **`AI/microsoft_phi-silica-3.6_v1/`** – Phi-3.6 LoRA fine-tuning

**Root-level integration**: `function_app.py` (Azure Functions) + orchestrators (`scripts/`) unify all three projects for production deployment.

## Quick Orientation

**Project boundaries** (each has its own venv):
- `quantum-ai/venv/` – quantum computing deps (qiskit, pennylane, pytorch)
- `talk-to-ai/venv/` – minimal chat deps (openai SDK only)
- `AI/microsoft_phi-silica-3.6_v1/venv/` – HuggingFace ML stack (transformers, peft, accelerate)
- Root `venv/` – Azure Functions runtime + shared utils

**Key execution points**:
- Always run orchestrators from repo root: `python .\scripts\autotrain.py`
- Always run project-specific scripts from their directory: `cd quantum-ai; python train_custom_dataset.py`
- Azure Functions uses root venv and imports from project src dirs via `sys.path.insert(0, ...)`

**State/output locations**:
- `data_out/` – all training outputs, logs, checkpoints, status.json files
- `datasets/` – source data only (never modified by training)
- `__azurite_db_*.json`, `__blobstorage__/` – local Azure emulator state (gitignored in production)

## Architecture Patterns

### 1. YAML-Driven Orchestration (Critical for All Projects)

**Never hardcode**: Models, backends, hyperparams live in YAML. Three orchestrators automate training:

```python
# Standard config loading pattern (relative from script location)
current_dir = Path(__file__).parent
config_path = current_dir.parent / "config" / "quantum_config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)
```

**Orchestrators** (`scripts/quantum_autorun.py`, `scripts/autotrain.py`):
- Define jobs in `quantum_autorun.yaml` / `autotrain.yaml` (root-level YAML files)
- Sequential execution with machine-readable status → `data_out/{quantum_autorun,autotrain}/status.json`
- Per-job timestamped logs → `data_out/autotrain/<job_name>/<timestamp>/stdout.log`
- Dry-run mode (`--dry-run`) validates all configs without execution
- List mode (`--list`) shows all available jobs
- Azure safety: QPU jobs require `azure_confirm_cost: true` to prevent accidental charges

**Job structure pattern** (autotrain.yaml example):
```yaml
jobs:
  - name: phi35_mixed_chat           # Required: unique identifier
    runner: hf                        # "hf" (full HuggingFace) or "local" (streamlined)
    config: AI/.../lora/lora.yaml     # Base config path
    dataset: datasets/chat/mixed_chat # Dataset directory
    save_dir: data_out/lora_training  # Output location
    epochs: 1                         # CLI override
    hf_model_id: microsoft/Phi-3.5-mini-instruct  # Model override
    max_train_samples: 64             # Limit for quick tests (null = full dataset)
```

**Command resolution hierarchy**: YAML base → CLI args → Job-specific overrides

### 2. Provider Abstraction (Chat System)

All chat providers implement `BaseChatProvider.complete(messages, stream)`:

```python
# talk-to-ai/src/chat_providers.py
class BaseChatProvider:
    def complete(self, messages: List[RoleMessage], stream: bool) -> Iterable[str] | str:
        raise NotImplementedError

# Providers: LocalEchoProvider, OpenAIProvider, AzureOpenAIProvider, LoraLocalProvider, QuantumChatProvider
```

**Auto-detection priority** (`detect_provider()`): Azure OpenAI → OpenAI → LoRA (if adapter exists) → Local fallback

**Adding new providers**: Subclass `BaseChatProvider`, implement `complete()`, add to `detect_provider()` chain in priority order

### 3. Azure Functions + Azurite Pattern

**Root-level integration** (`function_app.py`):
- Imports from `talk-to-ai/src` and `quantum-ai/src` via `sys.path.insert(0, ...)`
- Local dev uses Azurite emulator (files at repo root: `__azurite_db_*.json`, `__blobstorage__/`)
- Key endpoint: `/api/ai/status` returns provider health, ML deps, LoRA adapter readiness, orchestrator status

**Config**: `local.settings.json` → `AzureWebJobsStorage: UseDevelopmentStorage=true`

### 4. Dataset Registry System

**Centralized metadata**: `datasets/dataset_index.json` tracks all datasets (quantum CSVs, chat JSONL)
- Structure: `datasets/{quantum,chat,vision,raw,processed}/`
- Quantum: CSV with features+labels → PCA to `n_qubits` dims → StandardScaler normalization
- Chat: JSONL with Phi-3 template `{"messages": [{"role": "...", "content": "..."}]}`
- License tracking: Commercial (Dolly, OpenAssistant) vs non-commercial (Alpaca)

## Critical Workflows

### Quantum Training (Local → Azure Hardware Pipeline)

**Always test locally first** (CRITICAL cost-saving pattern):

```powershell
# 1. Local validation (FREE - required before Azure)
cd quantum-ai
python train_custom_dataset.py --preset heart --epochs 1

# 2. Orchestrated multi-job runs
python ..\scripts\quantum_autorun.py --dry-run              # Validate config
python ..\scripts\quantum_autorun.py --job heart_quick      # Run specific job

# 3. Azure hardware (PAID - requires safety flag)
# Edit quantum_autorun.yaml: azure_confirm_cost: true
python ..\scripts\quantum_autorun.py --job azure_ionq_qpu_test
```

**Circuit patterns** (enforced by YAML + code):
- Entanglement: `linear` (chain CNOTs), `circular` (ring), `full` (all-to-all)
- Layers: Input RY encoding → Variational (RY/RZ + entanglement) → PauliZ measurement
- Backend priority: `qiskit_aer` (local, unlimited) → `lightning.qubit` (fast >10 qubits) → Azure hardware

**Hardware validation** (Nov 2025 status):
- ✅ **Rigetti `rigetti.sim.qvm`**: Production-ready (1% accuracy vs hardware)
- ⚠️ **Quantinuum H-series simulators**: Known Azure bug—avoid until fixed
- Results: `quantum-ai/results/*.json`, visualize with `scripts/visualize_hardware_results.py`

### LoRA Training Pipeline

**Two runners** (`autotrain.yaml` specifies which):

```powershell
# Full HF stack (runner: hf)
cd AI\microsoft_phi-silica-3.6_v1
python .\scripts\train_lora.py --dataset ..\..\datasets\chat\dolly --config .\lora\lora.yaml --max-train-samples 64 --epochs 1

# Local streamlined runner (runner: local) - faster setup
python ..\..\scripts\run_local_lora_training.py

# Orchestrated multi-config training
cd ..\..
python .\scripts\autotrain.py --dry-run
python .\scripts\autotrain.py --job phi36_mixed_chat
```

**Config hierarchy**: `lora.yaml` base → CLI overrides → Job-specific overrides
**Output**: `data_out/lora_training/` (adapter, tokenizer, checkpoints, logs)

**Streaming dataset handling** (default, memory-efficient):
- Auto-computes `max_steps` from dataset size
- Use `--no-stream` only for small datasets (<500 samples)
- FilteringDataCollator removes invalid samples during training

### Chat Provider Usage

```powershell
cd talk-to-ai

# Local (FREE, offline-capable)
python .\src\chat_cli.py --provider local --once "Test"

# LoRA adapter (if trained)
python .\src\chat_cli.py --provider lora --model ..\..\data_out\lora_training\lora_adapter

# Azure OpenAI (requires 4 env vars)
$env:AZURE_OPENAI_API_KEY = "..."; $env:AZURE_OPENAI_ENDPOINT = "https://....openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"; $env:AZURE_OPENAI_API_VERSION = "2024-08-01-preview"
python .\src\chat_cli.py --provider azure

# Interactive commands: /new, /save (→ logs/chat_*.jsonl), /exit
```

### Azure Functions Local Dev

```powershell
# Start Azurite emulator (auto-configured in local.settings.json)
# Run Functions host
func host start  # or use VS Code task "func: host start"

# Test endpoints
curl http://localhost:7071/api/chat-web          # Web UI
curl http://localhost:7071/api/ai/status         # Health check (shows LoRA adapter status)
curl -X POST http://localhost:7071/api/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

**Key debugging pattern**: Check `/api/ai/status` → shows active provider, ML lib availability, LoRA adapter readiness, orchestrator status

### MCP Server (Quantum AI for AI Agents)

**Exposes 8 quantum tools** to AI agents via Model Context Protocol:

```powershell
cd quantum-ai
pip install -r mcp-requirements.txt
python quantum_mcp_server.py  # stdio server for VS Code/Claude

# Example VS Code config (.vscode/mcp.json)
{
  "quantum-ai": {
    "type": "stdio",
    "command": "python",
    "args": ["c:\\Users\\Bryan\\OneDrive\\AI\\quantum-ai\\quantum_mcp_server.py"]
  }
}
```

**Tools**: `create_quantum_circuit`, `simulate_quantum_circuit`, `train_quantum_classifier`, `connect_azure_quantum`, `submit_quantum_job`, `list_quantum_backends`, `estimate_quantum_cost`, `get_quantum_circuit_properties`

**Architecture**: ProcessPoolExecutor (CPU-bound quantum ops) + ThreadPoolExecutor (I/O) + LRU circuit cache (100 circuits, 3600s TTL)

## Testing & Validation

**Unit + integration tests** (`tests/`):
```powershell
pytest tests/test_autotrain_unit.py                    # Fast unit tests
pytest tests/test_autotrain_integration.py             # Full orchestrator tests
pytest tests/test_quantum_autorun_integration.py       # Quantum orchestrator tests
```

**Test patterns**:
- Unit tests: Dataclass creation, YAML parsing, command building (no subprocesses)
- Integration tests: Full job execution with mocked datasets and outputs
- Mock strategy: Use `unittest.mock.patch` for subprocess calls, temp directories for file I/O

**Validation scripts**:
```powershell
python .\scripts\validate_datasets.py --category chat --verbose    # Check JSONL integrity
python .\quantum-ai\scripts\visualize_hardware_results.py          # Charts from Azure job results
```

## Common Pitfalls

### 1. Azure Quantum Auth Failures
**Root cause**: Must call `azure_integration.connect()` before any backend ops
**Fix**: Check `quantum_config.yaml` matches Portal (subscription_id, resource_group, workspace_name) + run `az login`

### 2. LoRA Training OOM
**Symptom**: GPU/CPU out of memory during training
**Fix**: Reduce `finetune_train_batch_size` (2→1) or `finetune_train_seqlen` (1024→512) in `lora.yaml`, or use `--max-train-samples 64`

### 3. Chat Streaming Not Working
**Root cause**: Old openai SDK or missing env vars
**Fix**: `pip install --upgrade openai` (need ≥1.37.0), verify all 4 Azure OpenAI env vars set

### 4. Quantum Results Differ Across Backends
**Expected behavior**: Simulators show 1-2% variance, hardware shows 5-10% noise
**Validation**: Compare Bell state fidelity (should be >95% for `|00⟩ + |11⟩`)

### 5. Dataset Not Found
**Root cause**: Orchestrators use repo-root relative paths
**Fix**: Run from repo root, or check `datasets/dataset_index.json` for canonical paths

### 6. Module Import Errors in Azure Functions
**Root cause**: `function_app.py` imports from project src dirs—wrong working directory breaks paths
**Debug**: Check `/api/ai/status` → shows Python path, venv location, and ML library availability
**Fix**: Ensure `func host start` runs from repo root, not a subdirectory

## Cost Optimization Checklist

1. **Quantum**: Default `simulator.backend: qiskit_aer` in `quantum_config.yaml` (FREE, unlimited)
2. **Chat**: Use `--provider local` for development (no API costs)
3. **Training**: Start with `--max-train-samples 64 --epochs 1` on CPU (smoke test) before GPU scaling
4. **Azure**: Only provision resources when needed—simulators are FREE, QPU charges per gate-shot
5. **Free GPU alternatives**: Google Colab (12hrs/day), Kaggle Notebooks (30hrs/week), GitHub Codespaces (120 core-hrs/month)

## File Conventions

- **Config**: `*.yaml` (never hardcode in Python)
- **Logs**: Project-local dirs (`talk-to-ai/logs/`, `quantum-ai/results/`, `data_out/`)
- **Orchestrator status**: `data_out/{quantum_autorun,autotrain}/status.json` (machine-readable progress)
- **Persistence**: Chat → JSONL (`{"role": "user|assistant", "content": "...", "timestamp": "..."}`), Quantum → JSON with metadata

## Key Commands Reference

```powershell
# Quick setup (all free, ~500MB)
python .\scripts\quick_setup_datasets.py

# Orchestrators (dry-run before real runs)
python .\scripts\quantum_autorun.py --dry-run          # Validate quantum jobs
python .\scripts\autotrain.py --dry-run                # Validate LoRA jobs
python .\scripts\quantum_autorun.py --list             # List all quantum jobs
python .\scripts\autotrain.py --job phi36_mixed_chat  # Run specific LoRA job

# Local chat (no keys required)
python .\talk-to-ai\src\chat_cli.py --provider local --once "Test"

# Azure Functions local dev
func host start

# MCP server (for AI agents)
python .\quantum-ai\quantum_mcp_server.py

# Validation
python .\scripts\validate_datasets.py --verbose
pytest tests/
```

## When Adding New Features

1. **New quantum backend**: Update `quantum_config.yaml` → test with Bell state → validate with `scripts/visualize_hardware_results.py`
2. **New chat provider**: Subclass `BaseChatProvider` → implement `complete(messages, stream)` → add to `detect_provider()` priority chain
3. **New dataset**: Add to `datasets/dataset_index.json` → validate with `scripts/validate_datasets.py`
4. **New training preset**: Add to `quantum_autorun.yaml` or `autotrain.yaml` → test with `--dry-run` → document in orchestrator README
5. **New Azure Function endpoint**: Add route in `function_app.py` → update `/api/ai/status` response → test with `func host start`
6. **New script in `scripts/`**: Follow standard pattern: argparse CLI → `main()` function → `if __name__ == "__main__"` guard → comprehensive `--help` text

## Quantum AI (`quantum-ai/`)

**Setup & execution:**
```bash
cd quantum-ai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # Core: qiskit, pennylane, pytorch
pip install -r mcp-requirements.txt      # For MCP server: mcp>=0.9.0
python src/quantum_classifier.py         # Local simulation demo
python train_custom_dataset.py           # Train on datasets/quantum/*.csv
```

**Quantum AutoRun orchestrator** (`scripts/quantum_autorun.py`):
- **YAML-driven automation**: Define jobs in `quantum_autorun.yaml` with presets, hyperparams, and Azure backends.
- **Two modes**:
  - `train_custom_dataset`: Local simulator training (FREE, default)
  - `azure_hardware`: Submit to Azure Quantum (simulators FREE, QPU paid)
- **Safety**: Azure QPU jobs require `azure_confirm_cost: true` to prevent accidental charges.
- **Status tracking**: Generates `data_out/quantum_autorun/status.json` with per-job results, aggregates, and Azure metadata.
- **Usage**:
  ```powershell
  python .\scripts\quantum_autorun.py --dry-run              # Validate all enabled jobs
  python .\scripts\quantum_autorun.py --job heart_quick      # Run specific job
  python .\scripts\quantum_autorun.py --list                 # List configured jobs
  ```
- **VS Code tasks**: "Run: Quantum AutoRun (dry-run)" and "Run: Quantum AutoRun (all)".
- **Azure enrichment**: Successful Azure runs parse results and attach `azure_job_id`, `azure_counts`, `azure_success` to status meta.

**MCP server** (Model Context Protocol for AI agents):
- Run: `python quantum_mcp_server.py` (exposes 8 quantum tools via stdio).
- Tools: `create_quantum_circuit`, `simulate_quantum_circuit`, `train_quantum_classifier`, `connect_azure_quantum`, `submit_quantum_job`, `list_quantum_backends`, `estimate_quantum_cost`, `get_quantum_circuit_properties`.
- Circuit cache: Session-scoped LRU with TTL (100 circuits, 3600s); cleared on server restart.
- Architecture: ProcessPoolExecutor (2 workers) for CPU-bound quantum ops, ThreadPoolExecutor (4 workers) for I/O
- VS Code MCP config (`.vscode/mcp.json`):
  ```json
  { "quantum-ai": { "type": "stdio", "command": "python", "args": ["c:\\Users\\Bryan\\OneDrive\\AI\\quantum-ai\\quantum_mcp_server.py"] } }
  ```

**Azure Quantum integration** (`src/azure_quantum_integration.py`):
- **⚠️ OPTIONAL** - All quantum features work locally without Azure. Only use Azure for real quantum hardware access.
- Auth: `DefaultAzureCredential` (requires `az login` or env vars). Always call `connect()` before `list_backends()`/`submit_circuit()`.
- Config: Edit `quantum_config.yaml` → `azure.subscription_id`, `azure.resource_group`, `azure.workspace_name`.
- Deployment: Bicep templates in `azure/` (see `azure/DEPLOYMENT.md`). Create workspace via Portal or `az deployment group create`.
- **Free tier:** Microsoft Quantum simulators, `qiskit_aer`, `lightning.qubit` (unlimited local use).
- **Paid tier:** IonQ ~$0.00003/gate-shot, Quantinuum ~$0.00015/circuit.
- **Critical pattern:** ALWAYS test locally (`simulator.backend: qiskit_aer`) - never submit to paid hardware without validation.

**Circuit & model patterns** (enforced by YAML + code):
- Entanglement modes: `linear` (chain), `circular` (ring), `full` (all-to-all CNOT).
- Variational circuits: RY/RZ rotation layers → entangling CNOTs → measurement.
- Hybrid architecture: Classical preprocessing → quantum variational layer → classical output NN.
- Dataset integration: `train_custom_dataset.py` expects CSV with features + labels. Use PCA to reduce to `n_qubits` features, StandardScaler normalization.

**Hardware validation** (as of Nov 2025):
- ✅ Rigetti `rigetti.sim.qvm`: Production-ready, 1% accuracy vs hardware.
- ⚠️ Quantinuum H-series simulators: Known Azure bug (avoid until fixed). See `PROVIDER_COMPARISON_RESULTS.md`.
- Test flow: Bell state → GHZ → variational circuit. Results in `results/*.json`. Visualize with `scripts/visualize_hardware_results.py`.

## Talk-to-AI (`talk-to-ai/`)

**🆓 FREE DEFAULT: Local provider works offline with zero deps/keys**

**Provider auto-detection** (priority order):
1. Azure OpenAI: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`.
2. OpenAI: `OPENAI_API_KEY` (optional `OPENAI_MODEL`).
3. **Local fallback (FREE):** Zero deps, offline-capable (rule-based responses).

**Usage:**
```powershell
cd talk-to-ai
pip install -r requirements.txt  # openai>=1.37.0 (only for cloud providers)

# 🆓 FREE: One-shot local (no keys, works offline)
python .\src\chat_cli.py --provider local --once "Hello"

# 🆓 FREE: Interactive local mode
python .\src\chat_cli.py --provider local

# 💰 PAID: Interactive Azure OpenAI
$env:AZURE_OPENAI_API_KEY = "..."; $env:AZURE_OPENAI_ENDPOINT = "https://....openai.azure.com/"; $env:AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"
python .\src\chat_cli.py --provider azure

# Interactive commands: /new (reset), /save (write to logs/), /exit
```

**Persistence:**
- Conversations saved as JSONL in `logs/chat_<timestamp>.jsonl`.
- Format: `{"role": "user|assistant", "content": "...", "timestamp": "..."}`

## Phi-3.6 Fine-Tuning (`AI/microsoft_phi-silica-3.6_v1/`)

**💰 Note:** Full training requires GPU. Use CPU-friendly test mode for experimentation.

**Config structure:**
- LoRA: `lora/lora.yaml` (rank, dropout, target modules, training hyperparams).
- Soft prompt: `soft_prompt/soft_prompt.yaml` (prompt tuning params).
- Key settings in `lora.yaml`:
  - `finetune_train_nsamples: 8000`, `finetune_train_batch_size: 2`, `finetune_train_seqlen: 1024`.
  - Optimizer: `learning_rate: 0.0002`, `adam_beta1: 0.9`, `adam_beta2: 0.95`, `num_warmup_steps: 400`.
  - LoRA: `lora_dropout: 0.1`, `model: Phi-3.6-mini-instruct`.

**Execution:**
```powershell
cd AI\microsoft_phi-silica-3.6_v1
pip install -r requirements.txt

# 🆓 CPU-friendly test (no GPU required, 64 samples) - STREAMING MODE (default, handles large datasets)
python .\scripts\train_lora.py --dataset ..\..\datasets\chat\dolly --config .\lora\lora.yaml --max-train-samples 64 --max-eval-samples 16 --epochs 1

# 🆓 CPU-friendly test - NON-STREAMING MODE (faster for small datasets)
python .\scripts\train_lora.py --dataset ..\..\datasets\chat\dolly --config .\lora\lora.yaml --max-train-samples 64 --max-eval-samples 16 --epochs 1 --no-stream

# Dry-run (validate config, no training)
python .\scripts\train_lora.py --dry-run --dataset .\data --config .\lora\lora.yaml

# 💰 Full training (GPU required - use Colab free tier or Kaggle notebooks for free GPU access)
python .\scripts\train_lora.py --dataset ..\..\datasets\chat\dolly --config .\lora\lora.yaml
```

**VS Code quick tasks:**
- "Run: LoRA quick (streaming)" – smoke test with streaming dataset (default, memory-efficient)
- "Run: LoRA quick (non-stream)" – smoke test with non-streaming dataset (faster for small data)

**Free GPU alternatives:**
- Google Colab (free tier: ~12 hours GPU/day)
- Kaggle Notebooks (free tier: ~30 hours GPU/week)
- GitHub Codespaces (free tier: 120 core-hours/month)

**Dataset format:**
- JSONL with Phi-3 chat template: `{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}`
- Scripts support manifests (pointers to JSONL files) or direct JSONL dirs.
- Metrics → `save_dir` (local) or Azure Monitor/App Insights (if configured).

## Datasets (`datasets/`)

**🆓 All datasets are free and open-source**

**Quick setup:**
```powershell
python .\scripts\quick_setup_datasets.py  # Downloads quantum CSVs + Dolly 15k (~500 MB, 5 min)
```

**Structure:**
- `datasets/quantum/`: UCI ML datasets (heart_disease, ionosphere, sonar, banknote) as CSV.
- `datasets/chat/`: LLM fine-tuning (dolly, openassistant, alpaca) as JSONL.
- `datasets/raw/`: Original downloads (cache).
- `datasets/processed/`: Cleaned/transformed data.
- `datasets/dataset_index.json`: Metadata inventory.

**Manual downloads:**
```powershell
python .\scripts\download_datasets.py --category quantum                        # All quantum CSVs
python .\scripts\download_datasets.py --category chat --dataset dolly           # Dolly 15k (CC BY-SA, commercial OK)
python .\scripts\download_datasets.py --category chat --dataset openassistant   # OASST (Apache 2.0, larger)
python .\scripts\validate_datasets.py --verbose                                  # Validate integrity
```

**License awareness:**
- ✅ Commercial: Dolly (CC BY-SA 3.0), OpenAssistant (Apache 2.0), UCI datasets (attribution).
- ⚠️ Non-commercial: Alpaca (CC BY-NC 4.0).

**Integration:**
- Quantum: `train_custom_dataset.py` loads from `datasets/quantum/*.csv` with pandas.
- Phi-3.6: `--dataset ../../datasets/chat/dolly` (path to JSONL dir or manifest).

## Online IDE Compatibility

**GitHub Codespaces / VS Code Online:**
- All projects work in browser-based environments
- Free tier: 120 core-hours/month (60 hours on 2-core machine)
- Set up: `git clone` → run setup commands above
- Storage: Use free tier's 15GB for datasets

**Google Colab (for GPU tasks):**
```python
# Clone repo in Colab
!git clone https://github.com/<your-repo>/QAI.git
%cd QAI/AI/microsoft_phi-silica-3.6_v1
!pip install -r requirements.txt
# Run training with Colab's free GPU
!python scripts/train_lora.py --dataset ../../datasets/chat/dolly --config lora/lora.yaml --max-train-samples 256
```

**Kaggle Notebooks:**
- Free tier: 30 GPU hours/week
- Add datasets as Kaggle datasets (no download needed)
- Enable GPU in notebook settings

## Troubleshooting

**Azure Quantum connection fails:**
1. Verify: `az login` and `az account show` (correct subscription).
2. Check `quantum_config.yaml`: subscription_id, resource_group, workspace_name match Portal.
3. Confirm workspace exists: `az quantum workspace show -g rg-quantum-ai -n quantum-ai-workspace` or Portal.
4. Code pattern: Must call `azure_integration.connect()` before any `list_backends()`/`submit_circuit()` calls.

**Chat streaming not working:**
- Verify `openai>=1.37.0`: `pip list | findstr openai`.
- Check provider config: `--provider azure` requires all 4 env vars (`*_KEY`, `*_ENDPOINT`, `*_DEPLOYMENT`, `*_API_VERSION`).

**Out of memory (quantum):**
- Reduce `n_qubits` (4→3), `n_layers` (2→1), or `shots` (1024→128) in `quantum_config.yaml`.
- Use `simulator.backend: lightning.qubit` (faster than `qiskit_aer` for >10 qubits).

**JSONL validation errors:**
- Run `python .\scripts\validate_datasets.py --category chat --verbose` for details.
- Common fixes: Remove trailing blank lines, ensure valid JSON per line, verify `messages` array exists.

**LoRA training crashes:**
- **Streaming dataset errors**: Fixed in `train_lora.py` with auto-computed `max_steps` and FilteringDataCollator. Use `--no-stream` flag if issues persist.
- CPU: Use `--max-train-samples 64 --max-eval-samples 16 --epochs 1` for quick tests.
- GPU OOM: Reduce `finetune_train_batch_size` (2→1) or `finetune_train_seqlen` (1024→512) in `lora.yaml`.
- **No GPU?** Use Google Colab free tier (12 hours/day GPU) or Kaggle (30 hours/week GPU).
- **VS Code tasks**: Use "Run: LoRA quick (streaming)" or "Run: LoRA quick (non-stream)" for one-click smoke tests.

**Cost optimization:**
- Quantum: Default to `qiskit_aer` or `lightning.qubit` simulators (free, unlimited).
- Chat: Use `--provider local` for testing (no API costs).
- Training: Start with `--max-train-samples 64` on CPU before scaling to GPU.
- Azure: Only provision resources when you need paid hardware/services.

## Contribution checklist

When adding features or changing APIs:
1. Update the relevant project README (`quantum-ai/README.md`, etc.).
2. Document new config keys in YAML comments and this file.
3. Add CLI flags to help text (`--help` output).
4. For backends/providers: Update cost estimates (this file + `DEPLOYMENT.md`).
5. For datasets: Update `AI_DATASETS_CATALOG.md` and `dataset_index.json`.
6. Keep commands PowerShell-friendly (backticks, not semicolons; `.\path\`, not `./path/`).
