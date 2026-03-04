# Instructions Index

This folder contains path-scoped instruction modules for Copilot agents.

## Core modules

- `functions.instructions.md` — guidance for `function_app.py` API routes and diagnostics.
- `shared-python.instructions.md` — shared infra conventions (`shared/**/*.py`).
- `chat-web.instructions.md` — chat web frontend SSE behavior and integration notes.
- `talk-to-ai.instructions.md` and `talk-to-ai-python.instructions.md` — chat provider/CLI rules.
- `quantum-ai.instructions.md`, `quantum-ai-python.instructions.md`, `quantum-ai-mcp-python.instructions.md` — quantum workflows and MCP safety.
- `lora.instructions.md` and `lora-python.instructions.md` — LoRA/training conventions.

## Metadata governance modules

- `copilot-metadata.instructions.md` — authoring standards for `.github` metadata.
- `github-metadata.instructions.md` — documentation consistency rules for `.github/**/*.md`.

## Runtime-specific modules

- `aria-web-python.instructions.md` — Aria runtime Python endpoint/state guidance.
- `aria-web-js.instructions.md` — Aria runtime JS command/effect/UI guidance.
- `scripts-orchestrators.instructions.md` — status-driven orchestrator conventions.
- `tests-python.instructions.md` — testing quality and regression expectations.
- `dashboard-python.instructions.md` — dashboard Flask app, WebSocket, and monitoring scripts.
- `dashboard-js.instructions.md` — dashboard JavaScript UI helpers and WebSocket consumers.
- `cooking-ai-python.instructions.md` — cooking-ai recipe agent, providers, and CLI.
- `llm-maker.instructions.md` — LLM tool builder, registry, MCP server, and web UI.
- `config-yaml.instructions.md` — YAML/JSON config conventions for orchestrators and pipelines.
- `monetization-html.instructions.md` — monetization and subscription HTML page guidance.
- `docs-markdown.instructions.md` — documentation files and GitHub Pages content.
- `database-sql.instructions.md` — SQL schema definitions, migrations, stored procedures.
- `quantum-web-ui.instructions.md` — quantum web dashboard and visualization UI.
- `deployed-models.instructions.md` — model registry and versioned artifact management.
- `github-workflows.instructions.md` — GitHub Actions CI/CD workflow YAML files.
- `templates-emails.instructions.md` — notification email template conventions.
- `lora-azureml.instructions.md` — AzureML job YAMLs and cloud training configs.
- `quantum-azure.instructions.md` — Azure Quantum Bicep, DevOps, and cost monitoring.
- `chat-web-js.instructions.md` — chat-web JavaScript SSE consumer and TTS playback.

## Notes

- Add new modules only when the path scope has unique behavior.
- Keep modules focused; avoid cross-domain duplication.
- Update this index whenever instruction files are added or removed.
