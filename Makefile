# =============================================================================
# Aria Platform — Makefile
# =============================================================================
# Common targets for local development, testing, linting, and building.
#
# Prerequisites: python 3.11+, pip, docker, docker-compose
#
# Quick start:
#   make install      # install all dependencies
#   make dev          # start all services locally (Aria + Functions)
#   make test         # run unit tests
#   make lint         # run ruff + black --check
#   make format       # auto-format code
# =============================================================================

VENV_PYTHON  := $(wildcard .venv/bin/python)
PYTHON       ?= $(if $(VENV_PYTHON),$(VENV_PYTHON),python3)
PIP          ?= $(PYTHON) -m pip
PYTEST       ?= $(PYTHON) -m pytest
RUFF         ?= $(PYTHON) -m ruff
BLACK        ?= $(PYTHON) -m black
MYPY         ?= $(PYTHON) -m mypy
COMPOSE      ?= docker compose
TEST_PATH    ?= tests
ARIA_PORT    ?= 8080
FUNC_PORT    ?= 7071
GRADIO_PORT  ?= 7860
GRADIO_SHARE ?= false

.PHONY: all install install-qai dev start stop build test test-unit test-integration \
	lint format type-check clean docker-build docker-dev start-gradio \
	start-local-status start-functions-clean restart-functions-clean start-qai validate-mcp validate-mcp-json \
	agents agents-dry ai-automation aria-bot aria-bot-apply test-aria-bot sql-setup-local sql-status sql-reset-local sql-verify help

# Default target
all: lint test

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

## Install all project dependencies (runtime + dev)
install:
	$(PIP) install --upgrade pip
	@if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi
	@if [ -f requirements-dev.txt ]; then $(PIP) install -r requirements-dev.txt; fi
	@echo "✅ Dependencies installed."

## Install only runtime dependencies
install-prod:
	$(PIP) install --upgrade pip
	@if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi

# ---------------------------------------------------------------------------
# Development servers
# ---------------------------------------------------------------------------

## Start all services via Docker Compose (Aria web UI + Azure Functions)
dev:
	$(COMPOSE) -f docker-compose.dev.yml up --build

## Start Aria web server locally (without Docker)
start:
	@echo "🚀 Starting Aria web server on port $(ARIA_PORT)..."
	$(PYTHON) apps/aria/server.py --port $(ARIA_PORT)

## Start Azure Functions host locally (requires func CLI)
start-functions:
	@command -v func >/dev/null 2>&1 || { echo "❌ func CLI not found. Install: npm i -g azure-functions-core-tools@4"; exit 1; }
	func host start --port $(FUNC_PORT)

## Stop any listener on FUNC_PORT (deterministic, port-based)
start-functions-clean:
	@pids=$$(lsof -t -i:$(FUNC_PORT) -sTCP:LISTEN 2>/dev/null || true); \
	if [ -n "$$pids" ]; then \
		echo "🛑 Stopping process(es) on :$(FUNC_PORT): $$pids"; \
		kill -9 $$pids; \
	else \
		echo "ℹ️ No listener on :$(FUNC_PORT)"; \
	fi

## Restart Azure Functions host using a clean, port-based stop/start flow
restart-functions-clean: start-functions-clean
	@echo "🚀 Restarting Functions host on :$(FUNC_PORT)..."
	@command -v func >/dev/null 2>&1 || { echo "❌ func CLI not found. Install: npm i -g azure-functions-core-tools@4"; exit 1; }
	func host start --port $(FUNC_PORT)

## Start the lightweight local /api/ai/status adapter on FUNC_PORT
start-local-status:
	@if $(PYTHON) -c "import socket,sys; s=socket.socket(); rc=s.connect_ex(('127.0.0.1', $(FUNC_PORT))); s.close(); sys.exit(0 if rc==0 else 1)" >/dev/null 2>&1; then echo "ℹ️ Port $(FUNC_PORT) already in use; checking existing /api/ai/status..."; if $(PYTHON) -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$(FUNC_PORT)/api/ai/status', timeout=3).read(1)" >/dev/null 2>&1; then echo "✅ Local status adapter already running on :$(FUNC_PORT)."; exit 0; else echo "❌ Port $(FUNC_PORT) is occupied by a different service. Stop it or choose another port."; exit 1; fi; else $(PYTHON) local_dev_adapter.py --port $(FUNC_PORT); fi

## Install QAI integration service dependencies
install-qai:
	$(PIP) install -r mount/requirements.txt

## Start the QAI integration service on port 8000
start-qai: install-qai
	@echo "🚀 Starting QAI integration service on http://localhost:8000..."
	$(PYTHON) mount/app.py

## Start local Gradio demo UI
start-gradio:
	@echo "🚀 Starting local Gradio demo on port $(GRADIO_PORT)..."
	GRADIO_PORT=$(GRADIO_PORT) GRADIO_SHARE=$(GRADIO_SHARE) $(PYTHON) scripts/gradio_demo.py

## Bootstrap local SQL (SQLite) and verify connectivity
sql-setup-local:
	@QAI_SQL_URL=$${QAI_SQL_URL:-sqlite:///data_out/qai_local.db} $(PYTHON) scripts/sql_local_tools.py setup

## Read-only SQL status check (health + validation row count)
sql-status:
	@QAI_SQL_URL=$${QAI_SQL_URL:-sqlite:///data_out/qai_local.db} $(PYTHON) scripts/sql_local_tools.py status

## Reset local SQLite DB file and re-bootstrap sql_setup_check
sql-reset-local:
	@QAI_SQL_URL=$${QAI_SQL_URL:-sqlite:///data_out/qai_local.db} $(PYTHON) scripts/sql_local_tools.py reset

## End-to-end SQL verification (bootstrap + status + focused tests)
sql-verify:
	@$(MAKE) sql-setup-local
	@$(MAKE) sql-status
	@QAI_SQL_URL=sqlite:///:memory: $(PYTEST) -q tests/test_sql_integration.py tests/test_sql_engine_extended.py

## Start autonomous training orchestrator (dry-run by default)
start-orchestrator:
	$(PYTHON) scripts/autonomous_training_orchestrator.py --max-cycles 1 --dry-run

## Run aria-bot against the repo in dry-run mode
aria-bot:
	@echo "🤖 Running aria-bot in dry-run mode..."
	$(PYTHON) -m aria_bot --repo-root .

## Run aria-bot against the repo and apply safe changes
aria-bot-apply:
	@echo "🤖 Running aria-bot with --apply..."
	$(PYTHON) -m aria_bot --repo-root . --apply

## Stop all Docker Compose services
stop:
	$(COMPOSE) -f docker-compose.dev.yml down

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

## Run all tests
test:
	$(PYTEST) $(TEST_PATH) -q --tb=short

## Run only unit tests (fast, no cloud)
test-unit:
	$(PYTEST) $(TEST_PATH) -q --tb=short -m "not slow and not azure and not integration"

## Run integration tests
test-integration:
	$(PYTEST) $(TEST_PATH) -q --tb=short -m integration

## Run the focused aria-bot startup and entrypoint regression suite
test-aria-bot:
	$(PYTEST) tests/test_aria_bot.py tests/test_aria_bot_root_shim.py tests/test_aria_bot_dev_entrypoints.py -q

## Run tests with coverage report
test-coverage:
	$(PYTEST) $(TEST_PATH) -q --tb=short --cov=shared --cov=scripts \
		--cov-report=term-missing --cov-report=html:data_out/coverage_html

## Run a quick smoke test (import check)
smoke:
	$(PYTHON) -c "from shared.config import get_settings; s = get_settings(); print('Active provider:', s.active_provider())"
	$(PYTHON) -c "from shared.logging import configure_logging, get_logger; configure_logging(); get_logger('smoke').info('OK')"
	@echo "✅ Smoke test passed."

## Validate configured VS Code MCP stdio servers
validate-mcp:
	@$(PYTHON) scripts/validate_mcp_setup.py

## Validate configured VS Code MCP stdio servers with JSON output
validate-mcp-json:
	@$(PYTHON) scripts/validate_mcp_setup.py --json

# ---------------------------------------------------------------------------
# Repository inspection agents
# ---------------------------------------------------------------------------

## Run all repository inspection agents
agents:
	$(PYTHON) scripts/run_repo_agents.py

## Preview agent results without writing data_out/agents/*
agents-dry:
	$(PYTHON) scripts/run_repo_agents.py --dry-run

## Alias for agents
ai-automation: agents

# ---------------------------------------------------------------------------
# Code quality
# ---------------------------------------------------------------------------

## Run ruff linter and black formatter check
lint:
	$(RUFF) check $(TEST_PATH) shared/ scripts/ apps/aria/server.py
	$(BLACK) --check --quiet shared/ scripts/ apps/aria/server.py $(TEST_PATH)
	@echo "✅ Lint passed."

## Auto-format code with black and isort via ruff
format:
	$(RUFF) check --fix shared/ scripts/ apps/ $(TEST_PATH) || true
	$(BLACK) shared/ scripts/ apps/aria/server.py $(TEST_PATH)
	@echo "✅ Formatting complete."

## Run mypy type checks
type-check:
	$(MYPY) shared/ --ignore-missing-imports --no-error-summary || true
	@echo "✅ Type check done (warnings above are non-fatal)."

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

## Build Docker images
docker-build:
	docker build -f apps/aria/Dockerfile -t aria-server:local .
	docker build -f Dockerfile -t aria-functions:local .
	@echo "✅ Docker images built."

## Start services with docker-compose (same as dev)
docker-dev: dev

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

## Remove temporary build artifacts
clean:
	find . -type d -name __pycache__ -not -path './.git/*' | xargs rm -rf
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache data_out/coverage_html
	@echo "✅ Cleaned up."

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

## Show this help message
help:
	@echo ""
	@echo "Aria Platform — available make targets:"
	@echo ""
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## /  /'
	@echo ""
