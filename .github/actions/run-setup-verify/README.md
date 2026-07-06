# run-setup-verify

Composite action to run `make setup-verify` in CI, ensuring local setup guardrails stay healthy.

## Inputs

- `python-version` (optional, default: `3.12`)
- `dab-strict-values` (optional, default: `false`)
    - When `true`, exports `DAB_VERIFY_STRICT_VALUES=1` so DAB setup verification fails on placeholder connection-string values (for example `Database=undefined`).

## Usage

```yaml
- name: Setup guardrails
  uses: ./.github/actions/run-setup-verify
```

### Strict DAB placeholder checks

```yaml
- name: Setup guardrails (strict DAB values)
  uses: ./.github/actions/run-setup-verify
  with:
      dab-strict-values: "true"
```
