---
name: "LM Studio Coding Assistant"
description: "Aria-focused local coding workflow using LM Studio for code analysis, tests, docs, and refactors"
argument-hint: "Task + optional file path + desired output format"
agent: chat-provider
---

# LM Studio Coding Assistant

Use this prompt when you want local, privacy-friendly coding support in the Aria workspace via LM Studio.

## Operating Mode

- Prefer provider: `lmstudio`
- Fallback policy: LM Studio → Ollama → Azure OpenAI → OpenAI → local
- Keep outputs concise, actionable, and aligned with repository conventions
- Preserve existing APIs and route contracts unless explicitly asked to change them

## Inputs

- Task: `{{input}}`
- Optional file: `<path/to/file>`
- Optional goal: `[analyze | refactor | docs | tests | debug | design]`

## Expected Output Shape

1. **Diagnosis** — primary issues and likely root cause
2. **Patch Plan** — smallest safe changes to make
3. **Implementation Notes** — key edge cases and constraints
4. **Validation** — focused checks to run
5. **Risks/Follow-ups** — optional hardening steps

## Aria-Specific Guardrails

- Do not modify `datasets/`
- Keep SSE/event payload contracts stable
- Keep telemetry optional and non-blocking
- Maintain provider detection behavior in chat stack
- Prefer targeted tests over broad, expensive runs

## Handy Commands

- `bash scripts/llm_helper.sh analyze <file>`
- `bash scripts/llm_helper.sh docs <file>`
- `bash scripts/llm_helper.sh tests <file>`
- `python scripts/lm_studio_analyzer.py refactor <file>`

## Example Invocation

"Use LM Studio to analyze `function_app.py` for reliability and suggest a minimal patch that preserves endpoint behavior."
