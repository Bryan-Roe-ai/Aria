# Run Integration Contract Gate (Composite Action)

Wrapper action for `scripts/integration_contract_gate.sh`.

The underlying script now runs prechecks before contract/integration checks:

- `python3 scripts/validate_site_bundles.py --strict-metadata`
- `python3 scripts/validate_composite_actions.py`

## Inputs

- `strict-endpoints` (default: `false`)
  - `true`: runs `--strict-endpoints`

## Example

```yaml
- uses: ./.github/actions/run-integration-contract-gate

- uses: ./.github/actions/run-integration-contract-gate
  with:
    strict-endpoints: 'true'
```
