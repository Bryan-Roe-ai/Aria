# AI Starters (Local, No Cloud)

This folder contains 4 minimal examples:

1. `local_model_chat.py` — local model text generation (Transformers)
2. `fastapi_local_chat.py` — FastAPI web app chat endpoint powered by local model
3. `agent_with_tools.py` — simple AI-style agent with tools (search, calculator, file ops)
4. `sql_to_local_ai_orchestrator.py` — one script that runs SQL output through a local model

## Install

Use your preferred Python environment, then install:

- `transformers`
- `torch`
- `fastapi`
- `uvicorn`
- `psycopg2` or `psycopg` (for PostgreSQL)
- `pymysql` or `mysqlclient` (for MySQL)

## Run

### 1) Local model chat

`python examples/ai_starters/local_model_chat.py`

### 2) FastAPI chat app

`python examples/ai_starters/fastapi_local_chat.py`

Then open `http://127.0.0.1:8000`.

### 3) Agent with tools

`python examples/ai_starters/agent_with_tools.py`

### 4) SQL → local AI (single orchestrator)

`python examples/ai_starters/sql_to_local_ai_orchestrator.py --db-path <path-to.db> --query-file <query.sql>`

Example with inline SQL:

`python examples/ai_starters/sql_to_local_ai_orchestrator.py --db-path data.db --query "SELECT * FROM events LIMIT 20"`

PostgreSQL example:

`python examples/ai_starters/sql_to_local_ai_orchestrator.py --db-type postgres --db-url "postgresql://user:pass@localhost:5432/mydb" --query-file query.sql`

MySQL example:

`python examples/ai_starters/sql_to_local_ai_orchestrator.py --db-type mysql --db-url "mysql://user:pass@localhost:3306/mydb" --query "SELECT * FROM events LIMIT 20"`

## Notes

- Uses a small local model by default: `distilgpt2`.
- First run may download model files.
- No cloud API key required.
