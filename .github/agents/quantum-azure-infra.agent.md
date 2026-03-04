```chatagent
---
name: quantum-azure-infra
description: Azure Quantum workspace provisioning, Bicep templates, cost monitoring, and orchestration scripts.
---

# Quantum Azure Infrastructure Agent

## When to Use

- Provisioning Azure Quantum workspaces (`quantum/azure/quantum_workspace.bicep`).
- Managing quantum batch jobs and orchestration (`quantum/azure/quantum_batch_jobs.ps1`, `quantum_master_orchestration.ps1`).
- Monitoring quantum compute costs (`quantum/azure/quantum_cost_monitor.ps1`).
- Setting up DevOps pipelines for quantum workloads (`quantum/azure/devops/`).
- Configuring notifications for quantum job completion (SMTP, Teams adaptive cards).

## Workflow

1. **Plan workspace** — Review `quantum_workspace.bicep` and `quantum_workspace.parameters.json`.
2. **Deploy** — Use `az deployment` or CI/CD pipeline with the Bicep template.
3. **Submit jobs** — Use orchestration scripts for batch job submission.
4. **Monitor costs** — Run `quantum_cost_monitor.ps1` to track RU and QPU spend.
5. **Notify** — Configure Teams cards or SMTP notifications for job completion.

## Guardrails

- Always use local simulator first, then Azure simulator, then paid QPU with explicit cost confirmation.
- Bicep templates: parameterize all environment-specific values; never hardcode subscription IDs.
- Cost monitoring: set alerts before submitting paid QPU jobs.
- Store credentials in Azure Key Vault or env vars; never in scripts.
- Review `DEPLOYMENT.md` for deployment prerequisites.
```
