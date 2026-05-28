# Echo Agent — Responses Protocol (Streaming)

This sample demonstrates a minimal echo agent built with [azure-ai-agentserver-responses](https://pypi.org/project/azure-ai-agentserver-responses/) that streams responses word-by-word using Server-Sent Events (SSE).

## How It Works

The agent receives user input via the OpenAI Responses protocol (`POST /responses`) and echoes it back with a `🔊 Echo:` prefix. When `"stream": true` is set in the request, the response is delivered as SSE events — one delta per word — to demonstrate real-time streaming.

## Running Locally

### Prerequisites

- Python 3.10+
- Azure CLI installed and authenticated (`az login`)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the Agent

> **Tip:** Make sure the correct Python interpreter is selected in VS Code (Command Palette: **Python: Select Interpreter** or run command `python.setInterpreter`) so that debugging uses the right environment.

After installing dependencies, press **F5** in VS Code to start the agent and test it directly from the extension.

To start from the terminal instead:

```bash
python main.py
```

The agent starts on `http://localhost:8088/`. Open Agent Inspector (Command Palette: **AI Toolkit: Open Agent Inspector**) to connect and interact with the server.

### Test

#### 1. Test with curl

**Streaming:**

```bash
curl -N -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"model": "echo", "input": "Hello world!", "stream": true}'
```

**Non-Streaming:**

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"model": "echo", "input": "Hello world!"}'
```

#### 2. Test in Agent Inspector

Once the agent is running, open **Agent Inspector** in VS Code to interactively send messages and view responses.

Type the following message in Inspector:

```
Hello world!
```


## Deploying to Microsoft Foundry

To deploy your agent to Microsoft Foundry:

1. Open the Command Palette (`Ctrl+Shift+P`).
2. Run **Microsoft Foundry: Deploy Hosted Agent**.
3. The extension reads `agent.yaml` and auto-populates what it can. You may be prompted for:
   - **Agent name** -- the name registered with the hosting service.
   - **Dockerfile** -- auto-detected from workspace root, or select manually.
   - **Container registry** -- defaults to auto-created; optionally provide your own ACR.
   - **Resource size** -- CPU and memory allocation:

     | Option                        | CPU  | Memory |
     | ----------------------------- | ---- | ------ |
     | 0.25 CPU cores, 0.5 Gi memory | 0.25 | 0.5 Gi |
     | 0.5 CPU cores, 1 Gi memory    | 0.5  | 1.0 Gi |
     | 1 CPU cores, 2 Gi memory      | 1.0  | 2.0 Gi |
     | 2 CPU cores, 4 Gi memory      | 2.0  | 4.0 Gi |

4. The extension builds the container image in ACR, creates the agent version, and assigns required RBAC roles automatically.
