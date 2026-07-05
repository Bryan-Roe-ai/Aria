# Aria Module Documentation (Generated Draft)

> Generated from repository inspection. Review before committing.

## `agi_provider.py`

### Purpose
Provides abstraction logic for AGI or AI model provider integrations.

### Responsibilities
- Provider configuration
- Request orchestration
- AI backend selection
- Integration routing

### Related Files
- `chat_providers.py`
- `token_utils.py`
- `LMSTUDIO_AGI_INTEGRATION_IMPL.py`

---

## `chat_providers.py`

### Purpose
Defines chat-oriented provider integrations and model access helpers.

### Responsibilities
- Chat completion provider handling
- Provider registration
- Request forwarding

---

## `function_app.py`

### Purpose
Primary Azure Functions application module.

### Responsibilities
- Function registration
- HTTP/API entry points
- Runtime initialization
- Integration orchestration

### Dependencies
- Azure Functions runtime
- Shared provider modules
- Configuration files

---

## `run_automation.py`

### Purpose
Runs automation workflows locally.

### Responsibilities
- Automation execution
- Scheduling helpers
- Task orchestration
- Development-time workflow execution

### Related Scripts
- `run_continuous_automation.py`
- `setup_scheduled_automation.ps1`

---

## `local_dev_adapter.py`

### Purpose
Provides adapters and compatibility helpers for local development workflows.

### Responsibilities
- Local runtime integration
- Environment adaptation
- Development testing support

---

## `token_utils.py`

### Purpose
Utility helpers for token counting and token-related processing.

### Responsibilities
- Token accounting
- Usage estimation
- Shared token helper utilities

---

## `lora_infer_bridge.py`

### Purpose
Bridge module for LoRA-based inference workflows.

### Responsibilities
- LoRA inference execution
- Adapter integration
- Model invocation abstraction

---

## `aria_web/`

### Purpose
Web-facing interface components.

### Likely Responsibilities
- UI assets
- Web routes
- Frontend integration
- API consumption

---

## `aria_bot/` and `aria-bot/`

### Purpose
Bot-oriented automation and conversational integrations.

### Responsibilities
- Bot runtime integration
- Chat workflows
- Agent interaction logic

---

## `datasets/`

### Purpose
Dataset storage and training/evaluation assets.

### Responsibilities
- Model training inputs
- Benchmarking data
- Evaluation support

---

## `tests/`

### Purpose
Automated validation and regression testing.

### Notes
Testing configuration is defined in `pytest.ini`.
