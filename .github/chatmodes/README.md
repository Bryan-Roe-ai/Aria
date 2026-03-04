# Chatmodes Index

Chatmodes provide workflow-specific behavior profiles for Copilot.

## Status

Chatmode files are legacy in current tooling. Mode profiles are maintained in `.github/agents/`:

- `azure-function-codegen-and-deployment.agent.md`
- `azure-static-web-app.agent.md`
- `functions-api.agent.md`
- `chat-provider-stack.agent.md`
- `aria-runtime-debug.agent.md`
- `orchestrator-dryrun-status.agent.md`
- `quantum-safe-execution.agent.md`
- `testing-and-regression.agent.md`
- `docs-and-instructions-sync.agent.md`
- `release-readiness.agent.md`

## Authoring guidance

- Prefer focused modes over catch-all “do everything” modes.
- Keep prompts operational and measurable.
- Avoid hard-coding model names unless explicitly required.
- If a mode introduces new files or behavior constraints, also update related indexes/docs.
