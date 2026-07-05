---
runme:
    id: 01KWR9PPYY5K1164BQCBXFYQWW
    version: v3
---

# run-setup-verify

Composite GitHub Action that runs `make setup-verify` to enforce local setup guardrails.

## What it checks

- Recursive `venv` / `.venv` gitignore coverage (`make ignore-verify`)
- Data API Builder connection wiring (`make dab-verify`)

## Usage

```yaml {"id":"01KWR9PS2GPYMJ6CN62GP7GMSN"}
- name: Verify setup guardrails
  uses: ./.github/actions/run-setup-verify
```
