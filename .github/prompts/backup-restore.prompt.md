```prompt
---
agent: agent
description: "Create, verify, or restore a backup of models, configs, or training artifacts"
---
# Backup and Restore

## Task
Create or restore a backup of critical Aria artifacts.

## Context
- Backup manager: `scripts/backup_manager.py`
- Targets: `deployed_models/`, `config/`, `data_out/`
- Manifest: `backups/backup_manifest.json`

## Requirements
1. Identify what needs backing up (models, configs, training outputs).
2. Create timestamped backup with SHA-256 checksums.
3. Update the backup manifest after completion.
4. For restores: verify checksums match manifest before extracting.
5. Apply retention policy to clean old backups.

## Constraints
- Never overwrite existing backups; use timestamped names.
- Exclude secrets and credentials from archives.
- Write backups outside the git tree.
- Always verify checksums after backup and before restore.

## Success Criteria
- Backup created with all target files included.
- Checksums in manifest match actual file hashes.
- Restore produces identical files (verified by checksum).
```
