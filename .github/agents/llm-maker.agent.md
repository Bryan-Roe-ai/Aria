```chatagent
---
name: llm-maker
description: LLM tool creation, validation, registry, and MCP server for tools/llm-maker/.
---

# LLM Maker Agent

## When to Use

- Creating, validating, or registering custom LLM tools.
- Modifying the MCP server (`llm_maker_mcp_server.py`).
- Updating the web UI (`web_server.py`, `web_ui.html`, `website_maker_ui.html`).
- Website maker functionality (`src/website_maker.py`).
- Running or fixing tests (`tests/`, `test_llm_maker.sh`).

## Workflow

1. **Understand modules** — `src/tool_maker.py` creates tools, `src/tool_validator.py` validates schemas, `src/tool_registry.py` stores them, `src/tool_executor.py` runs them.
2. **Design tool schema** — Follow JSON-serializable schema conventions; validate before registering.
3. **Implement** — Keep tool logic in `src/`; MCP server wrappers in `llm_maker_mcp_server.py`.
4. **Test** — Run `bash test_llm_maker.sh` or `pytest tools/llm-maker/tests/`.
5. **Web UI** — Keep the web UI lightweight; server-render where possible.

## Guardrails

- Keep `tools/llm-maker/` self-contained with its own `requirements.txt`.
- Validate all tool schemas before registration; reject malformed input early.
- MCP server: keep tool schemas JSON-serializable; handle timeouts gracefully.
- Use relative paths from module root; never hardcode absolute paths.
- Config: `llm_maker_config.yaml` follows YAML conventions in `config/`.
```
