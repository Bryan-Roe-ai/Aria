```prompt
---
agent: agent
description: "Create, validate, or register a custom LLM tool in the tool maker"
---
# LLM Tool Creation

## Task
Design and register a new custom LLM tool using the tools/llm-maker framework.

## Context
- Tool maker: `tools/llm-maker/src/tool_maker.py`
- Validator: `tools/llm-maker/src/tool_validator.py`
- Registry: `tools/llm-maker/src/tool_registry.py`
- Executor: `tools/llm-maker/src/tool_executor.py`
- MCP server: `tools/llm-maker/llm_maker_mcp_server.py`
- Config: `tools/llm-maker/llm_maker_config.yaml`

## Requirements
1. Define the tool schema (JSON-serializable, typed parameters).
2. Validate the schema with `tool_validator.py` before registration.
3. Register in the tool registry.
4. Wire up MCP server exposure if the tool should be externally callable.
5. Write a test case in `tools/llm-maker/tests/`.

## Constraints
- Keep `tools/llm-maker/` self-contained.
- All tool schemas must be JSON-serializable.
- Handle execution timeouts gracefully.
- No hardcoded file paths; use config-driven paths.

## Success Criteria
- Tool validates and registers without errors.
- Tool executes correctly via `tool_executor.py`.
- MCP server exposes the tool if required.
- Tests pass.
```
