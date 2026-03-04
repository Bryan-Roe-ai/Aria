```instructions
---
name: "Copilot-Metadata"
description: "Authoring rules for prompts, chatmodes/agents, and instruction modules"
applyTo: ".github/**/*.md"
---
# Copilot Metadata Authoring Rules

Use this guidance when creating or editing Copilot metadata under `.github/`.

## Scope and intent

- Keep files purpose-specific and composable.
- Prefer many focused metadata files over one giant file.
- Use concise language with verifiable behavior and explicit boundaries.

## File types and naming

- Instructions: `domain[-language].instructions.md`
  - Examples: `functions.instructions.md`, `shared-python.instructions.md`
- Prompts: `verb-object.prompt.md`
  - Examples: `triage-bug.prompt.md`, `sync-docs.prompt.md`
- Chatmodes: `domain-purpose.chatmode.md` (legacy naming accepted)
  - Examples: `functions-api.chatmode.md`, `quantum-safe-execution.chatmode.md`
- Agents: `name.agent.md`

Use kebab-case for new files.

## Required metadata structure

- Instruction modules should use an `instructions` fence and include `name`, `description`, and `applyTo`.
- Prompt templates should use a `prompt` fence with minimal frontmatter and a reusable task template body.
- Chatmodes/agents should use a `chatagent` fence with `description` and optional `tools`.

## Content quality bar

- Keep examples cross-platform where possible.
- Never hardcode secrets.
- Avoid duplicated policy text across multiple files; place shared policy in one source and link to it.
- Preserve Aria guardrails:
  - `datasets/` is read-only.
  - Generated outputs go under `data_out/`.
  - Chat streaming uses SSE (`data: {json}` + `[DONE]`).
  - `/api/ai/status` is the readiness/diagnostics endpoint.
  - Quantum flow is simulator-first; paid QPU needs explicit cost confirmation.

## Maintenance checklist

- Update corresponding folder `README.md` indexes when adding/removing files.
- Verify references and links after metadata changes.
- Keep provider-order guidance aligned with canonical implementation.
- Keep workflow counts/docs in sync with actual `.github/workflows/*.yml` files.
```
