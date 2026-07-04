---
name: "AGI-Provider"
description: "Guidance for AGI provider implementation and reasoning system"
applyTo: "**/agi_provider.py"
---

# AGI Provider — Implementation Guidance

## Canonical module and shim boundaries

- Treat `ai-projects/chat-cli/src/agi_provider.py` as the source of truth.
- Treat the root-level `agi_provider.py` as a compatibility shim only; do **not** move logic there.
- Keep the shim exports and the canonical module exports aligned so legacy imports keep working.

## Reasoning pipeline contract

- `AGIProvider` wraps any `BaseChatProvider` with query analysis, optional task decomposition, reasoning, and self-reflection.
- Factory signature: `create_agi_provider(model, temperature, max_output_tokens, enable_chain_of_thought, enable_self_reflection, enable_task_decomposition, reasoning_depth, verbose)`.
- Preserve the pipeline order: `_analyze_query()` → `_decompose_task()` → `_reason()` → `_reflect_and_improve()`.
- Query complexity should remain coarse and predictable: simple (<10 words and no keywords), moderate, or complex.
- Intent detection should continue to cover movement, coding, explanation, creation, question, and general queries.
- Domain detection should continue to cover quantum, ai, aria, technical, and general.

## Behavioural expectations

- Decomposition templates should stay intent-specific:
	- coding: requirements → design → implement → edge cases → test
	- explanation: define → examples → relationships → summary
	- creation: concept → outline → details → review
	- question: direct → elaborate → examples → summary
- Self-reflection should check response completeness, answer length, and missing Aria tags for Aria-domain requests.
- When `domain == "aria"`, maintain movement/action tag injection such as `[aria:walk:left]`, `[aria:jump]`, `[aria:wave]`, and `[aria:dance]`.

## Safety, limits, and memory

- `_sanitize_input()` must strip control characters and enforce `MAX_INPUT_LENGTH=10000`.
- `_sanitize_for_logging()` should be used for log-safe output.
- Keep memory limits bounded: `MAX_HISTORY_SIZE=50`, `MAX_REASONING_CHAINS=10`, `MAX_GOALS=5`.
- `AGIContext` should continue to track `conversation_history`, `reasoning_chains`, `goals`, and `learned_patterns`.
- `ReasoningStep` should keep the fields `step_type`, `content`, `confidence`, and `metadata`.

## Validation

- Prefer targeted AGI provider tests when editing this file; use `pytest tests/ -m "not slow and not azure"` as the default baseline.
- If reasoning quality changes, verify the prompt and agent docs in `.github/prompts/agi.prompt.md` and `.github/agents/agi-reasoning.agent.md` still match the implementation.
