# AGENTS.md — Quick Reference for AI Coding Agents

This file is a focused, machine-friendly entry point for AI agents working in
this repository. Human-oriented guidance lives in `README.md` and
`.github/copilot-instructions.md`; this file emphasises **what to call** and
**what to read first** when acting autonomously.

## Repo at a glance

- Aria is an interactive AI character platform plus chat/quantum/LoRA projects.
- Three isolated sub-projects under `ai-projects/` (separate venvs).
- The Aria web UI server is at `apps/aria/server.py` (port 8080).
- Azure Functions integration layer at `function_app.py` exposes higher-level
  APIs that import from `ai-projects/`.

## First reads (in order)

1. `.github/copilot-instructions.md` — full architectural rules and patterns
2. `apps/aria/README.md` — Aria character system overview
3. `apps/aria/AUTO-EXECUTE.md` — auto-execute action sequence contract
4. `ai-projects/chat-cli/src/chat_providers.py` — provider detection chain
5. `function_app.py` — API endpoint definitions

## Aria HTTP API (port 8080)

| Method | Path                | Purpose                                                                                 |
| ------ | ------------------- | --------------------------------------------------------------------------------------- |
| GET    | `/api/aria/state`   | Current stage state (aria, objects, environment)                                        |
| GET    | `/api/aria/objects` | Object registry only                                                                    |
| GET    | `/api/aria/schema`  | **Action schema, valid gestures, limits** (use this to discover the contract)           |
| GET    | `/api/aria/health`  | Health snapshot: version, uptime, provider/model availability, entity counts, Aria pose |
| POST   | `/api/aria/command` | Natural language command → tags + inferred actions                                      |
| POST   | `/api/aria/execute` | Execute structured action sequence (plan or execute mode)                               |
| POST   | `/api/aria/object`  | Add/update/remove objects                                                               |
| POST   | `/api/aria/world`   | LLM-powered themed world generation                                                     |

### Action contract summary

Actions are JSON objects validated against `ARIA_ACTIONS` in `apps/aria/server.py`.
See `/api/aria/schema` at runtime for the canonical definition.

Core action types: `move`, `say`, `pickup`, `drop`, `throw`, `gesture`, `look`, `wait`.

Limits:

- Up to 25 actions per sequence
- Coordinates in `[0, 100]`
- `say.text` ≤ 200 chars
- `wait.duration` ≤ 30 seconds
- Allowed gestures: `wave, thumbs_up, clap, shrug, bow, nod`

### Fallback behaviour

When no LLM provider is configured, `/api/aria/command` uses a rule-based
parser plus `tags_to_actions` to convert legacy `[aria:*]` tags into structured
actions. Tag forms recognised include:

- `[aria:position:X:Y]` and `[aria:position:NAME]` (center/left/right/...)
- `[aria:gesture:NAME]` and `[aria:animation:NAME]`
- `[aria:say:TEXT]` and `[aria:expression:NAME]`
- `[aria:pickup:OBJ]`, `[aria:drop]`, `[aria:drop:OBJ]`
- `[aria:look:TARGET]`
- `[aria:throw:X:Y]`
- `[aria:wait:SECONDS]`
- `[aria:effect:NAME:...]` (sparkle/hearts/glow map to a wave gesture)

## Local LLM development

- `local.settings.json` Values are auto-injected by `func host start`; standalone entry
  points call `shared/local_settings.apply_local_settings()` (wired into `apps/aria/server.py`,
  `ai-projects/chat-cli/src/chat_cli.py`, `shared/chat_providers.py`, `shared/config.py`).
- Setup/probe helper: `scripts/setup_local_llm.py` — `--dry-run` (probe only, no writes/pulls),
  `--write` (persist provider/model), `--pull-model <name>`, `--provider auto|ollama|lmstudio`.
- Key env vars: `DEFAULT_AI_PROVIDER`, `ARIA_LLM_PROVIDER`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`,
  `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL`.
- On Windows when `python` is not on PATH, prefer `uv run python …` / `uv run pytest …` from repo root.
- Broken Linux devcontainer `.venv` on Windows (`.venv\lib64` access denied): remove `.venv`, then
  `uv sync --extra dev` (requires `[tool.setuptools.packages.find]` scoped to `shared*`).

## Safety rules for AI agents

- **Never modify `datasets/`** — read-only.
- Always run orchestrators with `--dry-run` before GPU/QPU execution.
- Quantum: simulator → Azure simulator → real QPU (only with `azure_confirm_cost: true`).
- All outputs go to `data_out/<orchestrator>/status.json`.
- Don't commit secrets — use `local.settings.json` (dev) or Azure App Settings.

## Test entry points

- Fast unit tests: `python scripts/test_runner.py --unit`
- Aria-specific unit tests: `pytest tests/unit/test_tags_to_actions.py`
- Aria-bot dry-run from repo root: `python -m aria_bot --repo-root .` or `make aria-bot`
- Quick repo validation: `python scripts/fast_validate.py`
- System health: `curl http://localhost:7071/api/ai/status | jq`

## Conventions

- Provider precedence (`detect_provider()` auto mode): explicit flag → LM Studio → Ollama → Azure OpenAI → OpenAI → local (`lora`/`agi`/`quantum` are explicit-only)
- Config precedence: YAML base < CLI flags < per-job YAML < env vars
- Chat dataset format: `[{"messages": [{"role": "...", "content": "..."}]}]`
- LoRA adapters must include both `adapter_config.json` and `adapter_model.safetensors`

## Learned User Preferences

- Prefer `uv run` from repo root when Python is not on PATH (common on Windows).
- Do not create new markdown docs for setup; use script `--help`/output or existing docs only.
- Commit only task-related files; exclude unrelated hook/workflow/deletion changes from feature commits.
- Do not commit unless explicitly requested.

## Learned Workspace Facts

- `scripts/setup_local_llm.py --dry-run` is the safe probe path (no file writes or model pulls).
- Gitignore pattern `local_settings.py` also ignores `shared/local_settings.py`; use `git add -f` when committing that module.
- Docs navigation: `docs/AI_REPO_INDEX.md` (code map) and `docs/QAI_DOCS_INDEX.md` (docs index).
- Ollama on Windows can be installed non-interactively via `winget install Ollama.Ollama`.

## Cursor Cloud specific instructions

The startup update script installs Python deps into `.venv` (Python 3.12). Use `.venv/bin/python` (or `make`, which auto-detects `.venv`). Everything runs fully offline with the `local` echo provider — no API keys required for setup or testing.

- **Aria web UI** (flagship, port 8080): `.venv/bin/python apps/aria/server.py --port 8080` (or `make start`). The root page `/` is a static stage demo with **no command box**; the natural-language command UI is at **`/auto-execute.html`** (text input + "Execute Actions" → `POST /api/aria/execute`). Backend command/execute endpoints work via curl regardless (see AGENTS.md API table). `ARIA_RENDER_MODE` defaults to `ue5` but the browser falls back to Three.js, so the stage still renders without UE5.
- **Azure Functions API** (port 7071): `func host start --port 7071` (or `make start-functions`). The `func` CLI (v4) is preinstalled in the VM snapshot at `~/.npm-global/bin` but is **not on the default PATH** — prepend it: `export PATH="$HOME/.npm-global/bin:$PATH"`. If `func` is ever missing, reinstall with `npm install -g azure-functions-core-tools@4 --unsafe-perm true`, then run `npm config delete prefix` to avoid an nvm/npmrc conflict. On startup the host logs `AzureWebJobsStorage ... Unhealthy` because Azurite isn't running; this is **expected and non-fatal** — HTTP-triggered endpoints (`/api/ai/status`, `/api/chat`, `/api/tts`, etc.) still respond. A lightweight fallback `make start-local-status` serves only `/api/ai/status`.
- **Tests/lint:** `.venv/bin/python scripts/test_runner.py --unit` is the fast suite. ~6 unit tests fail in this environment for reasons unrelated to dependencies (hardcoded `/workspaces/Aria/...` devcontainer paths, e.g. `test_validate_mcp_setup`, and tests assuming external services); the other ~2690 pass. `make lint` (ruff + black) currently reports many pre-existing findings across the repo — treat lint failures as code-quality state, not an environment problem.
