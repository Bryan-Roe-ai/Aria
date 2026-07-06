# Run Integration Contract Gate (Composite Action)

Wrapper action for `scripts/integration_contract_gate.sh`.

The underlying script runs the same deterministic gate used locally:

- `$PYTHON_BIN scripts/automate_core_files.py`
- `$PYTHON_BIN scripts/integration_smoke.py`
- `$PYTHON_BIN scripts/ci_orchestrator.py --integration-contract-tests`
- `$PYTHON_BIN scripts/ci_orchestrator.py --validate-all`
- In strict mode only: `curl` reachability check for `/api/ai/status`

`PYTHON_BIN` defaults to `python3`. Set it to `.venv/bin/python` when the checked-out repository already has a prepared virtual environment.

## Inputs

- `strict-endpoints` (default: `false`)
    - `true`: passes `--strict-endpoints` to the shell wrapper after the prechecks above.

## Strict endpoint environment

When `strict-endpoints` is `true`, the shell wrapper uses these optional environment variables:

| Variable                         | Default                               | Purpose                                                         |
| -------------------------------- | ------------------------------------- | --------------------------------------------------------------- |
| `INTEGRATION_AI_STATUS_ENDPOINT` | `http://localhost:7071/api/ai/status` | Endpoint that must become reachable                             |
| `RETRY_COUNT`                    | `30`                                  | Number of endpoint polling attempts                             |
| `RETRY_INTERVAL`                 | `1`                                   | Seconds between endpoint polling attempts                       |
| `START_FUNC_CMD`                 | unset                                 | Optional command to start a local Functions host before polling |

## Example

```yaml
- uses: ./.github/actions/run-integration-contract-gate

- uses: ./.github/actions/run-integration-contract-gate
  with:
      strict-endpoints: "true"
  env:
      PYTHON_BIN: .venv/bin/python
      INTEGRATION_AI_STATUS_ENDPOINT: http://localhost:7071/api/ai/status
```
