# 🚀 Welcome to Aria with GitHub Copilot

GitHub Copilot is fully integrated into this workspace. Here's how to get started:

## 1 minute setup

```bash
# Just open the project - VS Code will prompt to install recommended extensions
code .

# Extensions will install automatically
# (If not, Ctrl+Shift+X → "Show Recommended" → Install All)
```

## Open Copilot Chat

Press **`Ctrl+Shift+I`** (or **`Cmd+Shift+I`** on Mac)

## Pick an Agent

Use `@` to select one:

- **`@ai`** — Primary agent (auto-routes to specialists)
- **`@aria-character`** — Control the interactive character
- **`@autonomous-trainer`** — AI model training & lifecycle
- **`@full-stack-debugger`** — Debug issues across the stack
- **`@quantum-ai`** — Quantum circuits & Azure Quantum
- **`@chat-provider`** — Multi-provider chat integration

## Examples

Try these in Copilot Chat:

```
@aria-character Make Aria walk to the table and pick up the sphere

@autonomous-trainer Start training the next LoRA model

@full-stack-debugger Why is the /api/chat endpoint returning 500?

@AI_model_training Evaluate the latest model against the test dataset
```

## Where to Learn More

- **Full Setup Guide**: `.github/COPILOT_SETUP_GUIDE.md`
- **Quick Reference**: `.github/copilot-instructions.md`
- **Detailed Patterns**: `.github/copilot-instructions.full.md`
- **Component Guides**: `.github/instructions/`

## MCP Tools (Direct Integration)

Ask Copilot to use these specialized servers:

- **`@quantum-ai`** — Quantum circuit design & simulation
- **`@llm-maker`** — Safe code & website generation
- **`@lmstudio`** — Local LM Studio bridge for status, models, and one-shot prompts
- **`@task-complete`** — Task tracking

### LM Studio with Copilot

This workspace includes `scripts/lmstudio_mcp_server.py`, registered in `.vscode/mcp.json` as `lmstudio`.

What works:

- Copilot can call LM Studio as an MCP tool server
- Copilot can check LM Studio health, list models, and send a one-shot prompt

What does not change:

- GitHub Copilot Chat still uses GitHub-hosted models for the main assistant conversation
- LM Studio is available through MCP tools, not as a full replacement backend for Copilot itself

LM Studio endpoint (configured in `.vscode/mcp.json`):

```
http://192.168.1.153:1234/v1
```

Currently loaded models: `nvidia/nemotron-3-nano-4b`, `openai/gpt-oss-120b`,
`mistralai/devstral-small-2-2512`, `mistralai/magistral-small-2509`,
`mistralai/ministral-3-14b-reasoning`, `google/gemma-3-4b`

Example prompts:

- `Use the lmstudio MCP server to verify connectivity.`
- `Call lmstudio_list_models and show the results.`
- `Call lmstudio_chat with prompt "Explain this codebase" and model "mistralai/devstral-small-2-2512".`

## Quick Commands

Right in VS Code terminal:

```bash
# Validate setup
python3 scripts/pre_commit_check.py

# Run tests (Copilot can help fix failures!)
python3 scripts/test_runner.py --unit

# Start Aria character interface
cd apps/aria && python server.py

# Health check
curl http://localhost:7071/api/ai/status | jq
```

## Pro Tips

1. **Use agents for specialization** — Pick the most relevant agent for better results
2. **Provide context** — More details = better solutions
3. **Review code** — Ask Copilot to review your changes ('@github.copilot review my code')
4. **Use skills** — They load automatically based on context

## Troubleshooting

- **Chat not showing?** → Install GitHub Copilot Chat extension
- **Agents missing?** → Reload VS Code (Ctrl+Shift+P → "Reload Window")
- **MCP tools unavailable?** → Check `.vscode/mcp.json` is valid

---

**Ready to build with Copilot? Open Chat with Ctrl+Shift+I and type `@ai help me get started with Aria`. 🎉**
