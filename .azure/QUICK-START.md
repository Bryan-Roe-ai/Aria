# Quick Start — Deploy Aria to Azure

This guide walks through a minimal deployment to get Aria running on Azure Functions in ~45 minutes.

## Prerequisites

✓ **Azure CLI**: https://docs.microsoft.com/cli/azure/install-azure-cli  
✓ **Azure Account**: Active subscription with admin access  
✓ **Docker**: For building container images (optional if using azd)  
✓ **Git**: Latest commit should be on main branch  

## Step 1: Prepare (5 minutes)

```bash
cd /workspaces/Aria

# Verify system health
python scripts/test_runner.py --unit
python scripts/pre_commit_check.py

# Check git status
git status
# Should be clean; if not: git add -A && git commit -m "pre-deployment snapshot"
```

## Step 2: Authenticate to Azure (3 minutes)

```bash
# Login to Azure
az login
az account list  # Verify you can see your subscription

# Set default subscription
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

# Verify you're logged in
az account show
```

## Step 3: Choose Deployment Method

### Option A: Automated Deployment (Recommended)

Uses the provided `deploy-prod.sh` script which:
- Validates prerequisites
- Runs tests
- Builds container images
- Deploys Bicep infrastructure
- Verifies deployment

```bash
cd .azure

# Dry run first (shows what will be deployed)
bash deploy-prod.sh --dry-run

# Execute deployment
bash deploy-prod.sh \
  --resource-group aria-prod \
  --subscription "<YOUR_SUBSCRIPTION_ID>"
```

### Option B: Manual Deployment (Step-by-Step)

If you prefer to execute each step separately:

```bash
# 1. Create resource group
az group create --name aria-prod --location eastus

# 2. Deploy Bicep template
az deployment group create \
  --name aria-deploy \
  --resource-group aria-prod \
  --template-file .azure/main.bicep \
  --parameters @.azure/environments/prod.parameters.json \
  --parameters sqlAdminPassword="<YOUR_STRONG_PASSWORD>"

# 3. Get deployment outputs
az deployment group show \
  --name aria-deploy \
  --resource-group aria-prod \
  --query properties.outputs -o json
```

### Option C: Azure Developer CLI (azd)

If you have azd configured:

```bash
# Initialize
azd init

# Deploy
azd up

# Monitor
azd monitor
```

## Step 4: Verify Deployment (5 minutes)

Once deployment completes, verify everything is working:

```bash
# Get Function App URL
FUNCTION_APP_URL=$(az deployment group show \
  --name aria-deploy \
  --resource-group aria-prod \
  --query 'properties.outputs.functionAppUrl.value' -o tsv)

# Test health endpoint
curl "$FUNCTION_APP_URL/api/ai/status" | jq '.'

# Run verification script
bash .azure/verify-deployment.sh "$FUNCTION_APP_URL"
```

## Step 5: Configure Application Settings

Environment-specific configuration (secrets, API keys, etc.):

```bash
# Set database credentials
az functionapp config appsettings set \
  --name aria-prod \
  --resource-group aria-prod \
  --settings \
    QAI_DB_CONN="Server=tcp:aria-prod-sql.database.windows.net,1433;..." \
    OLLAMA_BASE_URL="http://ollama-service:11434/v1" \
    OLLAMA_MODEL="qwen2.5-coder:7b"

# If using Azure OpenAI
az functionapp config appsettings set \
  --name aria-prod \
  --resource-group aria-prod \
  --settings \
    AZURE_OPENAI_API_KEY="<YOUR_KEY>" \
    AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com/" \
    AZURE_OPENAI_DEPLOYMENT="<deployment-name>"

# If using Azure Speech TTS
az functionapp config appsettings set \
  --name aria-prod \
  --resource-group aria-prod \
  --settings \
    AZURE_SPEECH_KEY="<YOUR_KEY>" \
    AZURE_SPEECH_REGION="eastus"
```

## Step 6: Monitor & Observe (Ongoing)

```bash
# Tail live logs
az functionapp log tail \
  --name aria-prod \
  --resource-group aria-prod

# View in Azure Portal
# https://portal.azure.com -> Function Apps -> aria-prod

# Monitor with Application Insights
az monitor app-insights metrics show \
  --app aria-insights \
  --resource-group aria-prod \
  --metric RequestsPerSecond
```

## Step 7: Enable Auto-Scaling (5 minutes)

Configure auto-scaling to handle traffic spikes:

```bash
# View current plan
az appservice plan show \
  --name aria-prod-plan \
  --resource-group aria-prod

# For Elastic Premium plan, adjust scale limits
az functionapp config set \
  --name aria-prod \
  --resource-group aria-prod \
  --minimum-elastic-instance-count 1 \
  --maximum-elastic-worker-count 10
```

## Step 8: Setup Monitoring Alerts (10 minutes)

Get notified of issues:

```bash
# Alert: High error rate
az monitor metrics alert create \
  --name aria-high-errors \
  --resource-group aria-prod \
  --scopes \
    /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Insights/components/aria-insights \
  --condition "total requests | where resultCode >= '500' > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email --email-receiver your@email.com

# Alert: Slow response times
az monitor metrics alert create \
  --name aria-slow-responses \
  --resource-group aria-prod \
  --scopes \
    /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Web/sites/aria-prod \
  --condition "avg DurationMs > 5000" \
  --window-size 5m \
  --evaluation-frequency 1m
```

## Step 9: Setup CI/CD (Optional)

For automatic deployments on git push to main:

```bash
# Enable deployment from GitHub
az functionapp deployment github-actions add \
  --name aria-prod \
  --resource-group aria-prod \
  --repo-name Bryan-Roe/Aria \
  --repo-branch main \
  --service-principal-name aria-deploy
```

Or manually create `.github/workflows/deploy-prod.yml` in your repo.

## Verification Checklist

After deployment, verify:

- [ ] Health endpoint returns 200: `curl $FUNCTION_APP_URL/api/ai/status`
- [ ] Chat endpoint accepts requests: `curl -X POST $FUNCTION_APP_URL/api/chat`
- [ ] Provider is active: Check `/api/ai/status` for active provider
- [ ] No error rate spike in Application Insights
- [ ] Database is connected (check `/api/ai/status` -> db_pool)
- [ ] Logs are flowing to Application Insights

## Troubleshooting

### Function App Not Starting

```bash
# Check deployment errors
az functionapp log tail --name aria-prod --resource-group aria-prod

# Restart
az functionapp stop --name aria-prod --resource-group aria-prod
sleep 30
az functionapp start --name aria-prod --resource-group aria-prod
```

### Chat Endpoints Timing Out

```bash
# Check if Ollama is running
curl http://ollama-service:11434/api/tags

# If not, switch to local provider
az functionapp config appsettings set \
  --name aria-prod \
  --resource-group aria-prod \
  --settings DEFAULT_AI_PROVIDER=local
```

### High Cost

```bash
# Review resource usage
az monitor metrics show \
  --resource /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Web/serverfarms/aria-prod-plan \
  --metric FunctionExecutionUnits

# Scale down if over-provisioned
az appservice plan update \
  --name aria-prod-plan \
  --resource-group aria-prod \
  --sku EP1
```

## Next Steps

1. **Setup Monitoring**: Follow Step 8 for alerts
2. **Configure Backups**: Ensure SQL Database backups are enabled
3. **Test Failover**: Verify disaster recovery procedures
4. **Document Runbook**: Review PRODUCTION-RUNBOOK.md
5. **Train Team**: Walk through deployment and monitoring

## Support

For issues or questions:

1. Check PRODUCTION-RUNBOOK.md for common issues
2. Review Azure Portal logs: Function Apps → aria-prod → Log Stream
3. Check Application Insights: Monitor → Application Insights → aria-insights
4. Escalate to Platform Team if issue persists

---

**Deployment Time**: ~45 minutes  
**Estimated Cost**: $100-200/month (development tier)  
**SLA**: 99.5% uptime  

**Status**: ✅ Ready for Production  
**Last Updated**: June 1, 2026
