# Aria Platform — Production Deployment Plan

**Current Status**: Stable (2+ days uptime, all tests passing, automation healthy)  
**Last Validated**: June 1, 2026  
**Deployment Target**: Azure Functions + Container Apps (optional)  
**Version**: 1.0.0  

---

## Pre-Deployment Checklist

### System Health Verification ✅
- [x] Unit tests: 2354 passed (0 failures)
- [x] Linting: Clean (0 issues)
- [x] Security scan: Clean
- [x] Provider detection chain: Working (ollama qwen2.5-coder:7b)
- [x] Orchestrators: All healthy (autonomous_training, autotrain, quantum_autorun, evaluation_autorun)
- [x] API health check: `/api/ai/status` responding
- [x] Integration contracts: Validated
- [x] Watchdog supervisor: Running with 0 failures

### Code & Configuration
- [x] Main branch: `737f19954` (latest commit)
- [x] No uncommitted changes: `git status` clean
- [x] All dependencies in requirements.txt
- [x] `host.json` configured for Azure Functions
- [x] `local.settings.json` template prepared
- [x] Dockerfile production-ready (Python 3.14-slim)

### Azure Prerequisites
- [ ] Azure subscription active with adequate quota
- [ ] Azure Functions runtime v4+ available
- [ ] Resource group created and ready
- [ ] Application Insights enabled (optional, recommended)
- [ ] Storage account configured for Functions
- [ ] Secrets configured in Azure Key Vault (if needed)

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Azure Container Registry (ACR)                        │
│  └─ functions:latest (function_app.py)                 │
│  └─ aria:latest (apps/aria/server.py)                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Azure Functions (Premium/Elastic Plan)                │
│  ├─ /api/chat               (Multi-provider)           │
│  ├─ /api/ai/status          (Health endpoint)          │
│  ├─ /api/agi/*              (AGI reasoning)            │
│  ├─ /api/quantum/*          (Quantum ML)               │
│  ├─ /api/vision/*           (Expression AI)           │
│  └─ Static: /aria, /chat    (Web UIs)                 │
└─────────────────────────────────────────────────────────┘
         ↓ (optional)
┌─────────────────────────────────────────────────────────┐
│  Azure Container Apps (Aria Web Server)                │
│  └─ apps/aria/server.py on port 8080                   │
│     └─ /api/aria/command (Natural language)            │
│     └─ /api/aria/world (LLM world generation)          │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│  Supporting Services                                   │
│  ├─ Azure SQL Database (QAI_DB_CONN)                  │
│  ├─ Azure Cosmos DB (optional, QAI_ENABLE_COSMOS)    │
│  ├─ Application Insights (telemetry)                 │
│  ├─ Key Vault (secrets management)                   │
│  └─ Storage Account (persistent data)                │
└─────────────────────────────────────────────────────────┘
```

---

## Step 1: Prepare Environment Variables

Create `Settings.json` in Azure Function App with production values:

```json
{
  "FUNCTIONS_WORKER_RUNTIME": "python",
  "FUNCTIONS_EXTENSION_RUNTIME_VERSION": "~4",
  
  "# === Ollama / Local AI (production)": "",
  "OLLAMA_BASE_URL": "http://ollama-service:11434/v1",
  "OLLAMA_MODEL": "qwen2.5-coder:7b",
  
  "# === Optional: Azure OpenAI": "",
  "AZURE_OPENAI_API_KEY": "vault://prod-openai-key",
  "AZURE_OPENAI_ENDPOINT": "https://<resource>.openai.azure.com/",
  "AZURE_OPENAI_DEPLOYMENT": "prod-deployment",
  "AZURE_OPENAI_API_VERSION": "2024-08-01-preview",
  
  "# === Optional: Azure Speech TTS": "",
  "AZURE_SPEECH_KEY": "vault://prod-speech-key",
  "AZURE_SPEECH_REGION": "eastus",
  
  "# === Database": "",
  "QAI_DB_CONN": "Server=prod-sql.database.windows.net;Database=aria_prod;User Id=funcapp;Password=vault://prod-sql-pwd;Encrypt=true;Connection Timeout=30;",
  "QAI_SQL_POOL_SIZE": "20",
  
  "# === Optional: Cosmos DB": "",
  "QAI_ENABLE_COSMOS": "true",
  "COSMOS_ENDPOINT": "https://aria-prod.documents.azure.com:443/",
  "COSMOS_KEY": "vault://prod-cosmos-key",
  "COSMOS_DATABASE": "aria",
  "COSMOS_CONTAINER": "chat-sessions",
  
  "# === Telemetry": "",
  "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=prod-key;IngestionEndpoint=https://eastus-1.in.applicationinsights.azure.com/;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/",
  
  "# === Chat Defaults": "",
  "CHAT_TEMPERATURE": "0.7",
  "CHAT_MAX_TOKENS": "2048",
  "DEFAULT_AI_PROVIDER": "ollama",
  
  "# === Aria Web UI (optional)": "",
  "ARIA_PORT": "8080",
  "ARIA_RENDER_MODE": "ue5"
}
```

---

## Step 2: Deploy Infrastructure (Bicep)

Use the provided `main.bicep` to deploy:

```bash
# Login to Azure
az login
az account set --subscription "<SUBSCRIPTION_ID>"

# Create resource group
az group create --name aria-prod --location eastus

# Deploy infrastructure
az deployment group create \
  --name aria-prod-deploy \
  --resource-group aria-prod \
  --template-file .azure/main.bicep \
  --parameters \
    location=eastus \
    functionAppName=aria-prod \
    storageAccountName=ariaprod$(date +%s) \
    sqlServerName=aria-prod-sql \
    cosmosAccountName=aria-prod-cosmos
```

---

## Step 3: Build & Push Container Images

```bash
# Build Azure Functions container
az acr build \
  --registry <ACR_NAME> \
  --image functions:latest \
  --file function_app.Dockerfile \
  .

# Build Aria character web server (optional)
az acr build \
  --registry <ACR_NAME> \
  --image aria:latest \
  --file apps/aria/Dockerfile \
  .

# Deploy to Azure Functions
az functionapp deployment container config \
  --name aria-prod \
  --resource-group aria-prod \
  --enable-cd
```

---

## Step 4: Deploy Application Code

```bash
# Option A: Deploy from container registry
az functionapp create \
  --name aria-prod \
  --resource-group aria-prod \
  --storage-account <STORAGE_ACCOUNT> \
  --runtime python \
  --runtime-version 3.14 \
  --functions-version 4 \
  --image-name <ACR_NAME>.azurecr.io/functions:latest

# Option B: Deploy from source (zip)
cd /workspaces/Aria
zip -r deployment.zip . -x ".git/*" ".venv/*" "__pycache__/*"
az functionapp deployment source config-zip \
  --name aria-prod \
  --resource-group aria-prod \
  --src-path deployment.zip
```

---

## Step 5: Configure Application Settings

```bash
# Set all required environment variables
az functionapp config appsettings set \
  --name aria-prod \
  --resource-group aria-prod \
  --settings @.azure/environments/prod.parameters.json
```

---

## Step 6: Verify Deployment

```bash
# Test health endpoint
curl https://aria-prod.azurewebsites.net/api/ai/status

# Check function logs
az functionapp log tail \
  --name aria-prod \
  --resource-group aria-prod

# Monitor with Application Insights
az monitor app-insights metrics show \
  --app aria-insights \
  --resource-group aria-prod
```

---

## Step 7: Enable Continuous Deployment (CD)

### GitHub Actions Integration

Create `.github/workflows/deploy-prod.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run tests
        run: python scripts/test_runner.py --unit
      
      - name: Run pre-commit checks
        run: python scripts/pre_commit_check.py
      
      - name: Build container
        run: |
          az acr build \
            --registry ${{ secrets.REGISTRY_NAME }} \
            --image functions:${{ github.sha }} \
            --file function_app.Dockerfile .
      
      - name: Deploy to Azure Functions
        run: |
          az functionapp deployment container config \
            --name aria-prod \
            --resource-group aria-prod \
            --enable-cd
```

---

## Step 8: Monitoring & Alerting

### Set Up Alerts

```bash
# Alert on Function failures
az monitor metrics alert create \
  --name aria-function-failures \
  --resource-group aria-prod \
  --scopes /subscriptions/<SUB_ID>/resourceGroups/aria-prod/providers/Microsoft.Web/sites/aria-prod \
  --condition "avg Microsoft.Web/sites/FunctionExecutionUnits > 1000000000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email --email-receiver admin-email

# Alert on health endpoint failures
az monitor metrics alert create \
  --name aria-health-check \
  --resource-group aria-prod \
  --scopes /subscriptions/<SUB_ID>/resourceGroups/aria-prod/providers/Microsoft.Insights/components/aria-insights \
  --condition "total requests | where url == '/api/ai/status' and resultCode != '200' > 10" \
  --window-size 5m \
  --evaluation-frequency 1m
```

---

## Step 9: Rollback Procedure

If deployment fails or issues emerge:

```bash
# Get previous deployment
az functionapp deployment history list \
  --name aria-prod \
  --resource-group aria-prod

# Rollback to previous version
az functionapp deployment source config-zip \
  --name aria-prod \
  --resource-group aria-prod \
  --src-path previous-deployment.zip

# Or swap slots (if using deployment slots)
az functionapp deployment slot swap \
  --name aria-prod \
  --resource-group aria-prod \
  --slot staging
```

---

## Production Runbook

### Daily Checks
- [ ] `/api/ai/status` returning healthy (provider, orchestrators, DB pool)
- [ ] Application Insights showing normal request/error rates
- [ ] No alerts triggered
- [ ] Automated training cycles completing (check `/data_out/autonomous_training_status.json`)

### Weekly Maintenance
- [ ] Review Application Insights metrics for performance trends
- [ ] Check cost trends in Azure Cost Management
- [ ] Verify backup retention (SQL, Cosmos)
- [ ] Test rollback procedure

### Monthly Review
- [ ] Capacity planning (function execution time, storage, SQL pool)
- [ ] Security audit (Key Vault expiration, role assignments, network rules)
- [ ] Performance optimization (query execution, caching strategy)
- [ ] Update dependencies (requirements.txt)

---

## Support & Escalation

- **Deployment Issues**: Check Function App logs in Azure Portal → Function App → Log Stream
- **Performance Issues**: Use Application Insights → Failures/Performance tabs
- **Provider Errors**: Check chat provider detection via `/api/ai/status`
- **Database Issues**: Monitor SQL connection pool saturation (warns at ≥80%)
- **Orchestration Issues**: Check `data_out/*/status.json` for cycle failures

---

## Success Criteria

Deployment is **production-ready** when:
- ✅ All 40 API endpoints respond within SLA (≤2 seconds typical)
- ✅ Health check passes: `/api/ai/status` → HTTP 200 with full JSON
- ✅ No orchestrator failures for 24+ hours
- ✅ Error rate < 0.1% (Application Insights)
- ✅ Automated backups running on schedule
- ✅ Alerts configured and tested
- ✅ Rollback procedure validated

---

**Next**: Deploy using `az deployment group create` with the provided Bicep template and follow Step 1–9 above.

