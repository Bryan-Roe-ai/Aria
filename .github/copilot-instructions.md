# Aria — Copilot Quick Guide

*Last updated: March 2, 2026*

Aria is a multi-surface AI platform: interactive character UI, Azure Functions API layer, chat providers, LoRA pipelines, and quantum workflows.

## Big Picture (read this first)

- `function_app.py` is the main integration boundary (Azure Functions). It wires chat, streaming, TTS, health, vision, quantum, subscription, notification, and referral routes.
- `shared/` contains reusable infra (`chat_providers`, SQL/Cosmos clients, telemetry, chat memory). Prefer extending shared modules over duplicating logic.
- `tools/talk-to-ai/src/` is the canonical chat provider implementation; `shared/chat_providers.py` re-exports from it.
- `web/aria_web/` is a separate Python HTTP server for Aria character control (`/api/aria/*` endpoints), independent from Functions host.
- `quantum/` contains quantum ML + MCP tooling; use local/simulator flow before paid QPU.

## Critical Workflows (repo root)

- Fast validation: `python scripts/test_runner.py --unit` or `python scripts/test_runner.py --all`
- End-to-end health check: `python scripts/fast_validate.py`
- Start Functions API: `func host start`, then verify `GET /api/ai/status`
- Start Aria UI backend: `cd web/aria_web && python server.py` (default `127.0.0.1:8080`)
- Validate orchestrators before execution: `python scripts/autotrain.py --dry-run`, `python scripts/quantum_autorun.py --dry-run`, `python scripts/evaluation_autorun.py --dry-run`

## Fast Paths by Role

- New contributors: run `python scripts/test_runner.py --unit`, then `func host start`, then check `GET /api/ai/status` before changing internals.
- Automation agents: always run orchestrator `--dry-run` first, then read/write state via `data_out/<orchestrator>/status.json`.
- Both: treat `datasets/` as immutable inputs; write all generated outputs to `data_out/`.

## Project-Specific Conventions

- Treat `datasets/` as read-only. Write generated artifacts to `data_out/<component>/...`.
- Orchestrators are status-driven: persist machine-readable `status.json` under `data_out/` (see `scripts/master_orchestrator.py`, `scripts/ci_orchestrator.py`).
- Provider auto-detect order in `tools/talk-to-ai/src/chat_providers.py`: `lmstudio` → `azure` → `openai` → `local` (with explicit modes for `agi`, `quantum`, `lora`).
- LoRA adapters are valid only when both `adapter_config.json` and `adapter_model.safetensors` exist.
- Config precedence pattern: base YAML < CLI flags < per-job YAML overrides < environment variables.

## Integration Notes That Matter

- Functions chat routes (`/api/chat`, `/api/chat/stream`) call `detect_provider(...)`, prune context via `token_utils.prune_messages`, and optionally persist memory/telemetry.
- `/api/ai/status` is the authoritative readiness endpoint for provider/env/DB/Cosmos diagnostics.
- `web/chat-web/` frontend expects SSE semantics (`data: {json}` chunks + `[DONE]`) from chat streaming endpoints.
- `web/aria_web/server.py` keeps mutable `stage_state` and exposes `/api/aria/state`, `/api/aria/command`, `/api/aria/object`, `/api/aria/execute`, `/api/aria/world`.
- `function_app.py` dynamically imports from `tools/talk-to-ai/src` and `quantum-ai/src`; import errors are often path or env issues, not route logic bugs.

## Safety + Cost Guardrails

- Never hardcode secrets; use env vars or `local.settings.json` for local Functions dev.
- Quantum workflow: local simulator first, then Azure simulator, then paid QPU with explicit cost confirmation.
- Monitor SQL/Cosmos/telemetry behavior via `/api/ai/status` before debugging deeper runtime issues.

## Where to Edit (common tasks)

- API endpoints: `function_app.py`
- Provider behavior: `tools/talk-to-ai/src/chat_providers.py` (+ `shared/chat_providers.py` re-export)
- Aria command/state behavior: `web/aria_web/aria_controller.js`, `web/aria_web/server.py`
- Orchestrator logic: `scripts/*orchestrator*.py` + matching YAML in `config/`
- Shared persistence/observability: `shared/sql_engine.py`, `shared/cosmos_client.py`, `shared/telemetry.py`

## Instruction Modules

Use `.github/instructions/*.instructions.md` for path-specific rules (Functions, shared Python, quantum, talk-to-ai, LoRA, chat-web).