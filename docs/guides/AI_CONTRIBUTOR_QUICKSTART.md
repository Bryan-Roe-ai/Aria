# AI Contributor Quickstart

This guide is for contributors who want to work on Aria's AI stack quickly with minimal setup friction.

## What to run first

```bash
cp .env.example .env
cp local.settings.json.example local.settings.json
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Fast local AI checks

### Canonical integration flow (recommended order)

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python scripts/ci_orchestrator.py --integration-baseline
```

### 1) Chat provider smoke check (no keys required)

```bash
python ai-projects/chat-cli/src/chat_cli.py --provider local --once "hello"
```

### 2) Functions host AI health/status

```bash
func host start
curl http://localhost:7071/api/ai/status | python -m json.tool
```

### 3) Fast regression run

```bash
python scripts/test_runner.py --unit
```

## High-value AI code locations

- `function_app.py` — `/api/chat`, `/api/chat-web`, `/api/ai/status`, TTS routes
- `shared/chat_providers.py` — provider implementations and fallback flow
- `shared/chat_memory.py` — semantic memory storage and retrieval
- `shared/config.py` — provider/env settings normalization
- `ai-projects/chat-cli/src/` — terminal chat client and provider integration tests
- `scripts/autonomous_training_orchestrator.py` — autonomous train/evaluate loop
- `ai-projects/quantum-ml/` — quantum pipeline and MCP server tools

## Provider env quick reference

### OpenAI

- `OPENAI_API_KEY`

### Azure OpenAI

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

### Optional local TTS fallback

- `QAI_ENABLE_LOCAL_TTS=true`

## Before opening a PR

1. Run `python scripts/ci_orchestrator.py --integration-baseline`.
2. Run `python scripts/test_runner.py --unit`.
3. If provider/chat behavior changed, run:

    ```bash
    python -m pytest ai-projects/chat-cli/src/test_chat_providers.py tests/test_agi_provider.py -q --tb=short
    ```

4. Update `README.md` when adding/changing provider flags, environment variables, or onboarding commands.
