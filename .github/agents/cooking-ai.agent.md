```chatagent
---
name: cooking-ai
description: Cooking AI recipe agent development, provider integration, and testing.
---

# Cooking AI Agent

## When to Use

- Developing or debugging `cooking-ai/` recipe agent functionality.
- Adding or modifying providers in `cooking-ai/src/providers/`.
- Extending the CLI (`cooking-ai/src/main.py`) with new commands.
- Writing or fixing tests in `cooking-ai/tests/`.

## Workflow

1. **Understand scope** — `cooking-ai/` is a self-contained agent app with its own deps.
2. **Read entry point** — Start with `src/main.py` for CLI flow and `src/agents/recipe_agent.py` for agent logic.
3. **Implement** — Follow the existing provider pattern; new providers go in `src/providers/`.
4. **Test** — Run `pytest cooking-ai/tests/` to validate changes.
5. **Keep isolated** — Do not import from `shared/` or `tools/`; `cooking-ai/` is standalone.

## Guardrails

- Use `os.getenv` for API keys; never hardcode credentials.
- Handle provider init failures with fallback to `LocalProvider`.
- Keep `requirements.txt` scoped to what `cooking-ai/` actually needs.
- CLI commands should be documented in the interactive help text.
```
