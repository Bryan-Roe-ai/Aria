```instructions
---
name: "LLM-Maker"
description: "Guidance for tools/llm-maker/ tool builder, registry, and web UI"
applyTo: "tools/llm-maker/**"
---
# LLM Maker

- `tools/llm-maker/` provides tool creation, validation, execution, and a web UI for managing custom LLM tools.
- Core modules in `src/`: `tool_maker.py` (creation), `tool_validator.py` (validation), `tool_registry.py` (catalog), `tool_executor.py` (runtime), `website_maker.py` (site generation).
- Config: `llm_maker_config.yaml` — read with PyYAML; follow config precedence (base YAML < CLI < env vars).
- MCP server: `llm_maker_mcp_server.py` — expose tools over MCP protocol; keep tool schemas JSON-serializable.
- Web UI: `web_server.py` + `web_ui.html` + `web_ui_api_functions.js` — lightweight Flask/HTTP server.
- Tests: `tests/` and `test_llm_maker.sh` — validate before merging changes.
- Keep `tools/llm-maker/` self-contained with its own `requirements.txt`.
- Never hardcode file paths; use relative paths from module root or config-driven paths.
- Validate tool schemas before registration; reject malformed tools early with clear error messages.
```
