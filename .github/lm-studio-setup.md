# LM Studio Setup Guide for Aria

This guide helps you use LM Studio as your LLM provider for coding in the Aria workspace.

## Quick Start

### 1. Start LM Studio on Your Host Machine

- Download from [lmstudio.ai](https://lmstudio.ai/)
- Open the app
- Load a model runtime (e.g., Mistral 7B, Llama 2, GPT-OSS)
- Click "Start Server" (default: `http://localhost:1234`)

### 2. Test Connection

```bash
cd /workspaces/Aria
bash scripts/llm_helper.sh check
```

Expected output: `✓ LM Studio is running at ...`

## Usage

### Bash Commands (Quick Access)

```bash
# Check connection
bash scripts/llm_helper.sh check

# Single query
bash scripts/llm_helper.sh query "Your question here"

# Analyze code in a file
bash scripts/llm_helper.sh analyze function_app.py

# Generate documentation
bash scripts/llm_helper.sh docs apps/aria/server.py

# Generate tests
bash scripts/llm_helper.sh tests shared/chat_memory.py

# Debug an error
bash scripts/llm_helper.sh debug "ModuleNotFoundError: No module named 'xyz'"

# Explain a concept
bash scripts/llm_helper.sh explain "semantic memory"

# Interactive chat (multi-turn conversation)
bash scripts/llm_helper.sh chat
```

### Python Commands (Advanced)

```bash
# Analyze code from a file
python scripts/lm_studio_analyzer.py analyze function_app.py

# Analyze inline code
python scripts/lm_studio_analyzer.py analyze "
def hello():
    return 'world'
"

# Generate docstrings
python scripts/lm_studio_analyzer.py docs ai-projects/chat-cli/src/chat_cli.py

# Generate tests
python scripts/lm_studio_analyzer.py tests shared/chat_memory.py

# Get refactoring suggestions
python scripts/lm_studio_analyzer.py refactor shared/chat_providers.py

# Debug an error
python scripts/lm_studio_analyzer.py debug "NameError: name 'provider' is not defined"

# Design a solution
python scripts/lm_studio_analyzer.py design "I need to add streaming support to the chat endpoint"

# Explain a concept
python scripts/lm_studio_analyzer.py explain "AGI reasoning" --context "for Aria project"

# Raw prompt mode (most reliable for quick checks)
python scripts/lm_studio_analyzer.py query "Reply with OK only"

# Override timeout when model is slower
python scripts/lm_studio_analyzer.py query "Summarize this file" --timeout 180
```

### VS Code Integration

1. **Open Command Palette**: `Ctrl+Shift+P`
2. **Run Task**: `Tasks: Run Task`
3. **Select an LM Studio task**:
    - `LM Studio: Check Connection` - Verify LM Studio is running
    - `LM Studio: Start Chat` - Interactive conversation
    - `LM Studio: Analyze Current File` - Analyze the open file
    - `LM Studio: Generate Docs for File` - Create documentation
    - `LM Studio: Generate Tests for File` - Create unit tests
    - `LM Studio: Explain Selected Concept` - Explain any topic
    - `LM Studio: Debug Error Message` - Help debug errors
    - `LM Studio: Query Quick` - Send a quick query

Or add keyboard shortcut in `.vscode/keybindings.json`:

```json
{
    "key": "ctrl+shift+l",
    "command": "workbench.action.tasks.runTask",
    "args": "LM Studio: Start Chat"
}
```

## Common Workflows

### Code Review

```bash
bash scripts/llm_helper.sh analyze ai-projects/chat-cli/src/chat_providers.py
```

### Documentation Generation

```bash
bash scripts/llm_helper.sh docs function_app.py
```

### Test Generation

```bash
bash scripts/llm_helper.sh tests shared/chat_memory.py
```

### Debugging

```bash
bash scripts/llm_helper.sh debug "ConnectionError: Failed to connect to LM Studio"
```

### Architecture Design

```bash
python scripts/lm_studio_analyzer.py design "Add real-time collaboration to Aria character system"
```

### Learning About Concepts

```bash
bash scripts/llm_helper.sh explain "AGI reasoning chains"
bash scripts/llm_helper.sh explain "semantic embeddings"
bash scripts/llm_studio_analyzer.py explain "LoRA fine-tuning" --context "quantum ML workflows"
```

## Environment Variables

```bash
# Custom LM Studio endpoint (optional)
export LMSTUDIO_BASE_URL="http://127.0.0.1:1234/v1"

# In a dev container, this often needs to target the host bridge
export LMSTUDIO_BASE_URL="http://host.docker.internal:1234/v1"

# Optional: force a specific model id served by LM Studio
export LMSTUDIO_MODEL="openai/gpt-oss-20b"

# Make permanent (add to ~/.bashrc)
echo 'export LMSTUDIO_BASE_URL="http://host.docker.internal:1234/v1"' >> ~/.bashrc
echo 'export LMSTUDIO_MODEL="openai/gpt-oss-20b"' >> ~/.bashrc
source ~/.bashrc
```

## Troubleshooting

### Connection Fails

1. **Check LM Studio is running**:

    ```bash
    curl http://localhost:1234/v1/models
    ```

2. **Check LM Studio port** (if using non-default):

    ```bash
    export LMSTUDIO_BASE_URL="http://127.0.0.1:9999/v1"
    bash scripts/llm_helper.sh check
    ```

3. **Check firewall**:
    - Make sure port 1234 is not blocked
    - LM Studio should be accessible from the dev container

### Slow Responses

- Larger models take longer (5-30 seconds typical)
- Use a smaller model for faster responses (Mistral 7B is good)
- Set timeout: Use `--timeout 60` flag if available

### No Model Loaded

1. Open LM Studio
2. Load a model from the library
3. Wait for it to fully load
4. Start the server

### "No engine protocol runtime is registered" Error

This usually means the selected model id exists but is not currently loaded as a
chat-capable runtime in LM Studio.

1. Open LM Studio and load a chat-capable model runtime
2. Copy the active model id from LM Studio
3. Set it explicitly:

```bash
export LMSTUDIO_MODEL="<your-active-model-id>"
bash scripts/llm_helper.sh query "Reply with OK only"
```

## Integration with Aria Workflow

### Code Analysis Before Commit

```bash
# Analyze changes before committing
bash scripts/llm_helper.sh analyze function_app.py
```

### Feature Design

```bash
# Design new features
python scripts/lm_studio_analyzer.py design "Add voice command recognition to Aria"
```

### Documentation

```bash
# Generate docs for new modules
bash scripts/llm_helper.sh docs ai-projects/quantum-ml/src/quantum_llm/pipeline.py
```

### Testing

```bash
# Generate tests for new code
bash scripts/llm_helper.sh tests shared/subscription_manager.py
```

## Tips & Tricks

1. **Create aliases** for quick access:

    ```bash
    alias llm='bash /workspaceFolder/scripts/llm_helper.sh'
    llm query "your question"
    ```

2. **Pipe output to file**:

    ```bash
    bash scripts/llm_helper.sh analyze function_app.py > analysis.txt
    ```

3. **Combine with other tools**:

    ```bash
    # Analyze all Python files
    for f in $(find . -name "*.py" -type f); do
        echo "Analyzing $f..."
        bash scripts/llm_helper.sh analyze "$f" > "${f%.py}_analysis.txt"
    done
    ```

4. **Interactive prompt design**:

    ```bash
    # Start chat to iterate on prompt before using it in code
    bash scripts/llm_helper.sh chat
    ```

## Files Created

- `scripts/llm_helper.sh` - Bash wrapper for LM Studio queries
- `scripts/lm_studio_analyzer.py` - Python module for code analysis
- `.vscode/lm-studio-tasks.json` - VS Code tasks for LM Studio
- `.github/lm-studio-setup.md` - This guide

## Next Steps

1. ✅ **Start LM Studio** on your host machine
2. ✅ **Test connection**: `bash scripts/llm_helper.sh check`
3. ✅ **Try a query**: `bash scripts/llm_helper.sh query "test"`
4. ✅ **Integrate into workflow**: Use it for code review, testing, documentation
5. ✅ **Create custom prompts**: Adapt the scripts for your specific needs

## Questions?

For issues or feature requests, check:

- LM Studio docs: [lmstudio.ai/docs](https://lmstudio.ai/docs)
- Aria docs: `/workspaces/Aria/README.md`
- Chat provider setup: `/workspaces/Aria/ai-projects/chat-cli/README.md`
