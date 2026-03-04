```prompt
---
agent: agent
description: "Implement database backup and point-in-time recovery"
---
# Database Backup & Recovery
## Task
Implement database backup and recovery procedures.
## Requirements
1. Schedule full backups daily, incremental hourly. 2. Enable point-in-time recovery with WAL/log shipping.
3. Test restore procedures monthly. 4. Encrypt backups at rest.
5. Store backups in separate region.
## Constraints
- RPO < 1 hour. RTO < 4 hours. Encrypted backups. Test restores regularly.
## Success Criteria
- Backups automated. Point-in-time recovery works. Tested monthly. Encrypted and offsite.
```
