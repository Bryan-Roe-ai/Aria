```chatagent
---
name: backup-and-recovery
description: Automated backup of models, configs, and data with manifest tracking and restore capabilities.
---

# Backup & Recovery Agent

## When to Use

- Creating or restoring backups via `scripts/backup_manager.py`.
- Managing backup manifests and retention policies.
- Verifying backup integrity (checksums).
- Setting up automated backup schedules.

## Workflow

1. **Assess** — Identify what needs backing up: models in `deployed_models/`, configs in `config/`, data in `data_out/`.
2. **Backup** — Use `BackupManager` to create timestamped, checksummed archives.
3. **Verify** — Validate backup integrity via SHA-256 checksums in the manifest.
4. **Restore** — Extract from backup archive; verify checksums match manifest.
5. **Clean** — Apply retention policy to remove old backups.

## Guardrails

- Always verify checksums after backup and before restore.
- Write backups outside the git tree (default: `backups/` directory).
- Keep manifest (`backup_manifest.json`) up to date after every operation.
- Never overwrite existing backups; use timestamped names.
- Exclude secrets and credentials from backup archives.
```
