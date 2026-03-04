```instructions
---
name: "Quantum-Azure"
description: "Guidance for quantum/azure/ Bicep templates, DevOps pipelines, and cost monitoring scripts"
applyTo: "quantum/azure/**"
---
# Quantum – Azure Infrastructure

- `quantum/azure/` contains Bicep templates, deployment configs, DevOps pipelines, and cost monitoring scripts.
- `quantum_workspace.bicep` + `.parameters.json` — Azure Quantum workspace provisioning.
- `quantum_cost_monitor.ps1` — cost monitoring with budget alerts; run before paid QPU submissions.
- `quantum_master_orchestration.ps1` — batch job orchestration across providers.
- `quantum_batch_jobs.ps1` — individual job submission and status tracking.
- DevOps: `devops/` subfolder for CI/CD pipeline definitions.
- Notification: supports SMTP and Teams adaptive cards for job completion alerts.
- Execution priority: local simulator → Azure simulator → paid QPU (with explicit cost confirmation).
- Parameterize all environment values in Bicep (subscription ID, resource group, location).
- Store credentials in Azure Key Vault; never in scripts or checked-in config files.
- Review `DEPLOYMENT.md` for prerequisites and step-by-step deployment guide.
```
