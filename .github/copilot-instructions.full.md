# Aria — Copilot Instructions (Full Archive)

*Last updated: March 2, 2026*

This is the extended instruction archive for AI coding agents working in Aria. Use this when the short guide is not enough.

## Change Log

Add one dated bullet for each material update (scope, conventions, or corrected paths/commands).

- 2026-03-02: Consolidated duplicated sections into a single long-form guide.
- 2026-03-02: Added explicit role-based fast paths (new contributors and automation agents).
- 2026-03-02: Corrected provider guidance to match current canonical implementation and updated quantum MCP command path.

## 1) System Architecture

- Aria is a multi-surface system with two runtime surfaces:
  - Azure Functions API in `function_app.py`.
  - Separate Aria character HTTP server in `web/aria_web/server.py`.
- Canonical chat provider logic lives in `tools/talk-to-ai/src/chat_providers.py`; `shared/chat_providers.py` re-exports it for common imports.
- Shared infra in `shared/` covers SQL/Cosmos persistence, telemetry/tracing, and chat memory.
- Quantum workflows and MCP tooling are in `quantum/` (including `quantum/quantum_mcp_server.py`).

## 2) API + Service Boundaries

- Functions (`function_app.py`) owns `/api/chat`, `/api/chat/stream`, `/api/tts`, `/api/ai/status`, plus vision/quantum/subscription/referral routes.
- Aria web server (`web/aria_web/server.py`) owns `/api/aria/state`, `/api/aria/command`, `/api/aria/object`, `/api/aria/execute`, `/api/aria/world`.
- `web/chat-web/` consumes SSE contract from Functions streaming endpoints: `data: {json}` chunks and terminal `data: [DONE]`.
- `function_app.py` adds dynamic import paths for `tools/talk-to-ai/src` and `quantum-ai/src`; import failures are often environment/path issues rather than route logic defects.

## 3) Fast Paths by Role

- New contributors:
  - Run `python scripts/test_runner.py --unit`.
  - Start Functions with `func host start`.
  - Validate readiness at `GET /api/ai/status` before deeper changes.
- Automation agents:
  - Run `--dry-run` before orchestrator execution.
  - Treat `data_out/<orchestrator>/status.json` as source of truth for machine-readable state.
- Both:
  - Treat `datasets/` as immutable input.
  - Write generated artifacts only under `data_out/`.

## 4) Critical Developer Workflows

- Fast test entry points:
  - `python scripts/test_runner.py --unit`
  - `python scripts/test_runner.py --all`
- Broad health check:
  - `python scripts/fast_validate.py`
- Orchestrator validation first:
  - `python scripts/autotrain.py --dry-run`
  - `python scripts/quantum_autorun.py --dry-run`
  - `python scripts/evaluation_autorun.py --dry-run`
- Local Aria UI backend:
  - `cd web/aria_web && python server.py` (default `127.0.0.1:8080`)

## 5) Project-Specific Conventions

- Provider detection in `tools/talk-to-ai/src/chat_providers.py` auto mode: `lmstudio` → `azure` → `openai` → `local`.
- Explicit provider modes include `agi`, `quantum`, and `lora`.
- LoRA adapter is valid only if both files exist:
  - `adapter_config.json`
  - `adapter_model.safetensors`
- Config precedence pattern across orchestrators:
  - base YAML < CLI flags < per-job YAML overrides < environment variables.
- Orchestrators persist under `data_out/` and should expose status consistently as JSON.

## 6) Data + Artifact Discipline

- Never modify datasets in-place under `datasets/` during automation flows.
- Chat dataset pattern used across tools:
  - `datasets/chat/<name>/{train.json,test.json}`
  - rows shaped as `[{"messages": [{"role": "user|assistant", "content": "..."}]}]`
- Validate dataset shape with:
  - `python scripts/validate_datasets.py --category chat`

## 7) Integration Notes That Save Time

- Functions chat flow (`/api/chat`, `/api/chat/stream`) uses:
  - `detect_provider(...)`
  - context pruning via `token_utils.prune_messages`
  - optional SQL/Cosmos memory and telemetry persistence.
- `/api/ai/status` is the canonical diagnostics endpoint for provider/env/readiness, DB pool state, and optional services.
- For chat-web regressions, verify SSE format compatibility before changing client parsing.

## 8) Safety + Cost Guardrails

- Never hardcode secrets; use env vars or `local.settings.json` for local Functions runs.
- Quantum execution order:
  - local simulator first,
  - then Azure simulator,
  - paid QPU only with explicit cost confirmation.
- Start QPU runs with low shots and cost estimate review.
- Use `/api/ai/status` for SQL/Cosmos/telemetry sanity before deep debugging.

## 9) Where to Edit (Common Tasks)

- API routes and cross-feature wiring: `function_app.py`
- Provider behavior and fallback logic: `tools/talk-to-ai/src/chat_providers.py`
- Shared provider import surface: `shared/chat_providers.py`
- Aria command/state behavior: `web/aria_web/aria_controller.js`, `web/aria_web/server.py`
- Orchestrators: `scripts/*orchestrator*.py` + matching config in `config/`
- Shared persistence/observability: `shared/sql_engine.py`, `shared/cosmos_client.py`, `shared/telemetry.py`

## 10) Onboarding Commands (First 5 Minutes)

- `python --version`
- `python scripts/system_health_check.py`
- `python tools/talk-to-ai/src/chat_cli.py --provider local --once "Hello"`
- `python scripts/test_runner.py --unit`

## 11) Instruction Modules

- Path-specific guidance is maintained under `.github/instructions/`:
  - `functions.instructions.md`
  - `shared-python.instructions.md`
  - `quantum-ai*.instructions.md`
  - `talk-to-ai*.instructions.md`
  - `lora*.instructions.md`
  - `chat-web.instructions.md`
