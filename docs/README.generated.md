# Aria (Generated Documentation Draft)

Aria is a multi-service AI automation platform that combines Azure Functions, local automation workflows, AI provider abstractions, and experimental tooling into a single repository.

This draft documentation was generated from repository inspection and should be reviewed before publication.

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- Azure Functions Core Tools (for function execution)

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Or with `uv`:

```bash
uv sync
```

### Configure Environment

Copy and configure:

```bash
cp .env.example .env
cp local.settings.json.example local.settings.json
```

Populate environment variables without committing secrets.

### Run Locally

#### Azure Functions

```bash
func start
```

#### Local Automation

```bash
python run_automation.py
```

#### Continuous Automation

```bash
python run_continuous_automation.py
```

## Repository Structure

```text
core/                  Core application logic
functions/             Azure Function handlers
function_app.py        Main Azure Functions entry point
aria_web/              Web-facing application components
aria_bot/              Bot integrations
shared/                Shared utilities
tools/                 Automation and tooling scripts
datasets/              Dataset and training assets
tests/                 Automated tests
docs/                  Project documentation
```

## Key Technologies

- Python
- Azure Functions
- Docker
- TypeScript
- Gradio
- LM Studio integrations

## Development Tooling

The repository includes:

- `pytest`
- `flake8`
- `pre-commit`
- Docker-based local environments
- CI configuration under `.circleci/`

## Existing Documentation

Additional implementation-specific documentation exists in:

- `AUTONOMOUS_AGENT_GUIDE.md`
- `ENVIRONMENT_SETUP.md`
- `AUTOMATIC_AUTOMATION_GUIDE.md`
- `REVENUE_INTEGRATION.md`

## Contributing

Contribution guidance is available in `CONTRIBUTING.md`.

## License

The repository includes a `LICENSE` file at the repository root.
