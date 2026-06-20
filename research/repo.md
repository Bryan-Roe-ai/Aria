# Aria Repository Research Report

**Repository:** `Bryan-Roe/Aria`  
**Branch analyzed:** `main` (current + default)  
**Report date:** 2026-06-20

## 1) Executive summary

Aria is a multi-surface AI platform combining:
- an interactive character runtime (`apps/aria`),
- a unified Azure Functions API gateway (`function_app.py`),
- modular AI backends (`ai-projects/*`), and
- continuous/autonomous training + orchestration scripts (`scripts/*`).

The repository is architected for **provider flexibility** (LM Studio/Ollama/cloud/local), **safe degradation** (fallback to local behavior when optional dependencies fail), and **automation-first operations** (status files, health endpoints, background orchestrators).

A notable strength is the explicit split between read-only datasets and generated outputs (`datasets/` vs `data_out/`), plus guardrail hooks and runtime checks. The primary complexity/risk is operational coupling: the platform spans web UI, Azure Functions, provider routing, training pipelines, and optional infra (SQL/Cosmos/telemetry), so verification discipline is essential when changing shared contracts. 

## 2) Scope and method

This report was produced by direct analysis of repository sources and configuration in the current workspace, focusing on architecture, runtime behavior, safety controls, and operational quality signals.

## 3) System architecture map

### 3.1 Top-level composition

The project is explicitly organized into:
- `apps/aria/` character system,
- `ai-projects/chat-cli/` multi-provider chat layer,
- `ai-projects/quantum-ml/` experimental quantum workflows,
- `AI/` LoRA workspace,
- `shared/` cross-cutting infrastructure,
- `scripts/` orchestration/testing utilities,
- `function_app.py` as integration/API layer.

This separation is documented in the repo README and reinforced by runtime imports in `function_app.py`.

### 3.2 Integration pattern

`function_app.py` initializes a centralized module registry (`AIProjectsRegistry`) and then binds route handlers for chat, AGI, streaming SSE, status, and automation helper endpoints. It also safely imports optional components (telemetry, tracing, SQL/Cosmos, safety middleware, memory) with graceful fallbacks rather than hard failure.

**Implication:** the API layer is designed as an operational facade over optional subsystems, prioritizing availability over strict dependency hard-failure.

## 4) Runtime surfaces and contracts

### 4.1 Azure Functions surface (`function_app.py`)

Key route groups include:
- `/api/chat`, `/api/chat/stream` (JSON + SSE),
- `/api/agi/analyze|reason|stream|status|persistence`,
- `/api/chat-web` static frontend serving,
- utility/observability routes (`resource-monitor`, `model-deployer/status`, `evaluation-results`, etc.).

Important behavior traits:
- strict request parsing/sanitization for chat payloads,
- optional guardrails for input/output safety,
- optional semantic memory retrieval + injection,
- structured pruning/token-budget path via `prune_messages`,
- SSE stream protocol with explicit `[DONE]` sentinel.

### 4.2 Aria character server (`apps/aria/server.py`)

The Aria server exposes a separate HTTP surface (default port 8080) with:
- stage state/schema/health reads,
- natural-language command parsing,
- structured action execution,
- world generation.

The action contract is explicit and validated (`move`, `say`, `pickup`, `drop`, `throw`, `gesture`, `look`, `wait`), with parameter constraints and sequence limits. The parser supports LLM path first + deterministic fallback path.

**Operational note:** this dual-surface model (Functions API + Aria server API) enables specialization but introduces contract-sync overhead.

## 5) Provider strategy and AI fallback behavior

Provider selection in `ai-projects/chat-cli/src/chat_providers.py` is deterministic and well-layered:

- **Explicit modes** (including `agi`, `quantum`, `lora`) are honored first.
- In auto mode: **LM Studio → Ollama → Azure OpenAI → OpenAI → local echo**.
- Local mode still prefers local model runtimes before local echo fallback.

The provider module includes:
- alias normalization,
- runtime availability checks with thread-safe caches,
- OpenAI-compatible message normalization,
- quota/rate-limit handling with user-friendly degradation,
- local deterministic behavior for no-key/no-network environments.

This is a robust design for developer ergonomics and partial-connectivity environments.

## 6) Autonomous training and lifecycle automation

`scripts/autonomous_training_orchestrator.py` implements a long-running controller with:
- PID lock + graceful signal handling,
- status + heartbeat files under `data_out/`,
- dataset discovery,
- simulated/iterative cycle metrics,
- plateau-aware promotion workflow,
- optional scheduled quantum-LLM training step.

Configuration in `config/autonomous_training.yaml` shows aggressive automation defaults (`continuous: true`, interval scheduling, optimization toggles, monitoring thresholds, optional quantum block).

**Strength:** strong operational observability via status artifacts.  
**Risk:** many knobs; config governance and validation are critical for reproducibility.

## 7) Testing and verification posture

`scripts/test_runner.py` provides suite-based orchestration (unit/integration/all/quantum/chat/database/autotrain), summary parsing, watch mode, and machine-readable report emission in `data_out/test_runner/`.

This encourages consistent local verification and supports CI-style evidence capture even outside CI.

## 8) Safety and policy enforcement

Safety posture is reinforced across three layers:

1. **Documentation/policy conventions** (don’t modify `datasets/`, secrets handling, dry-run expectations).
2. **Runtime guardrails** (AI safety middleware, validation schemas, fallback behavior in API flows).
3. **Hook gates** in `.github/hooks/` (dataset immutability, secrets checks, quantum gates, checklist/commit hygiene).

The `secrets-leak-guard` hook currently executes a Python-only command for `PreToolUse`, `PostToolUse`, and `UserPromptSubmit`, with a warn-first default unless `ARIA_SECRETS_BLOCK=true`.

## 9) Key risks and opportunities

### Risks
- **Cross-surface drift:** behavior can diverge between `apps/aria/server.py` and `function_app.py` if contracts evolve unevenly.
- **Operational complexity:** many optional integrations can produce subtle environment-specific behavior.
- **Automation blast radius:** autonomous loops require careful guardrails to avoid noisy/expensive runs.

### Opportunities
- Add a single generated contract snapshot for shared API/route schema validation across both surfaces.
- Expand targeted smoke gates for provider fallback behavior and SSE framing consistency.
- Add periodic drift checks between README-declared endpoints and live route inventory.

## 10) Conclusion

Aria is a mature, operations-aware AI platform with pragmatic fail-safe design patterns and clear modular boundaries. Its biggest challenge is not feature breadth, but **coordination across many moving runtime layers**. The repo already has strong foundations (status files, hooks, provider fallbacks, test orchestration); continued investment in contract synchronization and automated drift detection will yield the highest reliability gains.

---

## Sources

- **[S1]** `/workspaces/Aria/README.md`
- **[S2]** `/workspaces/Aria/function_app.py`
- **[S3]** `/workspaces/Aria/shared/chat_providers.py`
- **[S4]** `/workspaces/Aria/ai-projects/chat-cli/src/chat_providers.py`
- **[S5]** `/workspaces/Aria/apps/aria/server.py`
- **[S6]** `/workspaces/Aria/scripts/autonomous_training_orchestrator.py`
- **[S7]** `/workspaces/Aria/config/autonomous_training.yaml`
- **[S8]** `/workspaces/Aria/scripts/test_runner.py`
- **[S9]** `/workspaces/Aria/.github/hooks/secrets-leak-guard.json`
- **[S10]** `/workspaces/Aria/.github/hooks/scripts/secrets_leak_guard.py`
- **[S11]** `/workspaces/Aria/AGENTS.md` (workspace attachment context)
- **[S12]** `/workspaces/Aria/.github/copilot-instructions.md` (workspace attachment context)
