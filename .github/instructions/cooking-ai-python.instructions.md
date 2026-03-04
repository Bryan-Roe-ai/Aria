```instructions
---
name: "Cooking-AI-Python"
description: "Guidance for cooking-ai/ recipe agent, providers, and CLI"
applyTo: "cooking-ai/**/*.py"
---
# Cooking AI – Python

- `cooking-ai/` is a standalone agent app with its own `requirements.txt` and test suite.
- Entry point: `src/main.py` — CLI with `/search`, `/extract`, `/exit` interactive commands.
- Provider pattern: `detect_provider(name)` tries GitHub Models first, then falls back to `LocalProvider()`.
- Agent: `src/agents/recipe_agent.py` handles recipe search/extraction logic.
- Providers live in `src/providers/`; each must expose a consistent chat/completion interface.
- Tests: `cooking-ai/tests/` — run with `pytest cooking-ai/tests/`.
- Keep `cooking-ai/` self-contained; do not import from `shared/` or `tools/` unless explicitly bridging.
- Use `os.getenv` for API keys (`GITHUB_MODELS_API_KEY`, `GITHUB_TOKEN`); never hardcode.
- Handle provider init failures gracefully with fallback and user-visible warnings.
```
