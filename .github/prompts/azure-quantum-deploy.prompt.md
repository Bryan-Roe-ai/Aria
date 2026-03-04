```prompt
---
agent: agent
description: "Deploy an Azure Quantum workspace with Bicep templates and cost monitoring"
---
# Azure Quantum Deploy

## Task
Provision or update an Azure Quantum workspace and configure cost monitoring.

## Context
- Bicep template: `quantum/azure/quantum_workspace.bicep`
- Parameters: `quantum/azure/quantum_workspace.parameters.json`
- Cost monitor: `quantum/azure/quantum_cost_monitor.ps1`
- Orchestration: `quantum/azure/quantum_master_orchestration.ps1`
- Deployment guide: `quantum/azure/DEPLOYMENT.md`

## Requirements
1. Review and parameterize the Bicep template for the target environment.
2. Deploy using `az deployment group create` or CI/CD pipeline.
3. Configure cost monitoring alerts before submitting paid jobs.
4. Set up job notification channels (SMTP or Teams adaptive cards).
5. Validate workspace connectivity with a test job on the simulator.

## Constraints
- Always test on local simulator first, then Azure simulator, then paid QPU.
- Never hardcode subscription IDs, resource group names, or credentials.
- Set cost alerts before any paid QPU submission.
- Store credentials in Azure Key Vault or env vars.

## Success Criteria
- Workspace deploys successfully from Bicep template.
- Cost monitoring alerts are active.
- Test job completes on simulator without errors.
- Notification channels configured and verified.
```
