# Aria Architecture (Generated Draft)

> This document was generated from repository contents and should be reviewed before merging.

## Overview

Aria is a multi-component AI automation platform centered around Python services, Azure Functions, local automation runners, and modular AI integrations. The repository combines:

- Azure Function endpoints (`function_app.py`, `functions/`, `function_app_domains/`)
- Local automation and orchestration scripts (`run_automation.py`, `run_continuous_automation.py`)
- AI provider abstractions (`agi_provider.py`, `chat_providers.py`)
- Web and bot integrations (`aria_web/`, `aria_bot/`, `aria-bot/`)
- Dataset, model, and experimentation tooling (`datasets/`, `deployed_models/`, `notebooks/`)

## Primary Entry Points

### Azure Function Runtime

- `function_app.py`
- `host.json`
- `function_app_domains/`

The Azure Functions runtime appears to be the primary hosted execution layer. `function_app.py` contains the main application registration and endpoint definitions.

### Local Development and Automation

- `app.py`
- `run_automation.py`
- `run_continuous_automation.py`
- `local_dev_adapter.py`

These scripts support local execution, scheduled workflows, and development-time orchestration.

### AI Provider Layer

- `agi_provider.py`
- `chat_providers.py`
- `token_utils.py`
- `lora_infer_bridge.py`

These modules encapsulate provider-specific logic and token handling for AI model integrations.

## High-Level Component Flow

```text
Client/UI
  │
  ├── aria_web/
  ├── aria_bot/
  └── Azure Function endpoints
           │
           ▼
    function_app.py
           │
           ├── AGI provider abstractions
           ├── automation runners
           ├── datasets/models
           └── shared utilities
                    │
                    ▼
             External AI services
```

## Key Directories

| Directory | Purpose |
| ------------ | --------------------------------------------- |
| `core/` | Core runtime and shared application logic |
| `functions/` | Azure Function handlers and execution modules |
| `shared/` | Shared utilities and reusable helpers |
| `tools/` | Automation and utility tooling |
| `config/` | Configuration assets and runtime settings |
| `docs/` | Existing project documentation |
| `examples/` | Demonstration and usage examples |
| `datasets/` | Training and evaluation datasets |
| `tests/` | Automated test suite |

## Runtime and Tooling

### Python

Primary runtime is Python with dependency management defined in:

- `pyproject.toml`
- `requirements.txt`
- `uv.lock`

### TypeScript

The repository also contains TypeScript configuration:

- `main.ts`
- `tsconfig.json`

### Containerization

- `Dockerfile`
- `docker-compose.dev.yml`
- `function_app.Dockerfile`

## Configuration Sources

Configuration is distributed across:

- `.env.example`
- `local.settings.json.example`
- `agent.yaml`
- `host.json`
- `config/`

Sensitive values should be supplied through environment variables and local settings files.

## External Integrations

The repository references integrations for:

- Azure Functions
- Azure ML
- Gradio
- LM Studio (`LMSTUDIO_AGI_INTEGRATION_IMPL.py`)
- LoRA inference (`lora_infer_bridge.py`)
- Docker-based local development

## Observations

- The repository includes multiple experimental and generated assets.
- Existing documentation is extensive but distributed across many standalone markdown files.
- Some directories appear to support autonomous-agent workflows and automation scheduling.
- `main.py` is currently empty and does not appear to be an active entry point.
