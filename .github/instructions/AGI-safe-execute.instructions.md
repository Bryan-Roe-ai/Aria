---
description: "Use when planning or executing shell/terminal commands with AGI workflows. Enforces stricter safety defaults for destructive operations, secret handling, and cost-risk commands before execution."
---
# AGI Safe Execute Defaults

Apply these defaults whenever terminal/shell commands are considered.

## Safety-first command policy

- Prefer read-only inspection commands before write/mutate commands.
- Prefer non-destructive alternatives first (`--dry-run`, `--check`, `--diff`, preview flags).
- Never run destructive filesystem commands on broad paths unless the user explicitly requests it and scope is tightly constrained.
- Never execute remote scripts directly from the network (`curl|bash`, `wget|sh`) without explicit user intent and verification.
- Never print or persist secrets from environment variables, config files, or command output.
- For expensive operations (cloud, QPU, long-running training), perform a dry run and state expected cost/risk before execution.

## Block-by-default command patterns

Treat these as blocked unless user explicitly requests and confirms scoped intent:

- Recursive root/system deletion patterns (e.g., `rm -rf /`, wildcard wipes outside target folder)
- Destructive disk operations (`mkfs`, `fdisk`, `dd` targeting block devices)
- Privilege escalation + destructive combo (`sudo rm -rf ...`)
- Process-wide destructive kill patterns (`kill -9 -1`, broad `pkill` with unsafe patterns)

## Execution hygiene

- Use the smallest scope path possible; avoid ambiguous relative paths for destructive actions.
- Echo intent in plain language before running any mutating command.
- After mutating commands, run a focused verification check and report outcome.
- If a safer path exists, choose it by default and explain why briefly.

## Emergency override (narrowly scoped)

For high-risk commands that are intentionally approved, use a short-lived exact-command override:

- `AGI_SHELL_OVERRIDE_ACK=I_UNDERSTAND_THE_RISK`
- `AGI_SHELL_OVERRIDE_SHA256=<sha256 of exact command text>`
- `AGI_SHELL_OVERRIDE_EXPIRES_EPOCH=<unix epoch seconds>`
- `AGI_SHELL_OVERRIDE_NONCE=<unique one-time token, min 12 chars>`
- `AGI_SHELL_OVERRIDE_REQUEST_ID=<approval/request identifier, min 8 chars>`

Notes:

- Override applies only to high-risk patterns (not catastrophic patterns).
- Override must match the exact command text hash (includes goal + explanation fields).
- Override must be time-bound and near-term; stale/far-future overrides are rejected.

### Optional: Request-ID format validation (Layer 6)

To standardize request-ID patterns and improve audit traceability, set an optional regex pattern:

- `AGI_SHELL_OVERRIDE_REQUEST_ID_PATTERN=<regex>`

Example patterns:

```bash
# Format: REQ-YYYYMMDD-XXXX (recommended default)
AGI_SHELL_OVERRIDE_REQUEST_ID_PATTERN='^REQ-\d{8}-\d{4}$'

# Format: TICKET-123456
AGI_SHELL_OVERRIDE_REQUEST_ID_PATTERN='^TICKET-\d{6}$'

# Format: REQ_YYYY_MM_DD_seq (with underscore separators)
AGI_SHELL_OVERRIDE_REQUEST_ID_PATTERN='^REQ_\d{4}_\d{2}_\d{2}_\d{3}$'
```

Format validation results in audit logs:

- **No pattern set** (default): `(request-id format check not configured)`
- **Valid match**: `(request-id format matches pattern)`
- **Format mismatch**: `(request-id format mismatch: expected <pattern>, got <actual>)`
- **Pattern error**: `(pattern error: <msg>, allowing override)`

⚠️ **Important**: Format validation is informational only. Invalid formats do NOT block the override—they are logged for audit purposes only. This enables gradual adoption without operational friction.

## Preferred workflow

1. Inspect current state.
2. Propose minimally risky command sequence.
3. Execute smallest safe step.
4. Verify and report evidence.
5. Continue iteratively until objective is complete.
