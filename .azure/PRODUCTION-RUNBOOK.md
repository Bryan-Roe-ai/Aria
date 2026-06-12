# Aria Platform — Production Runbook

## Service Overview

**Aria** is an interactive AI character platform with autonomous learning, multi-provider chat, and quantum ML integration running on Azure Functions.

**SLA Target**: 99.5% uptime  
**RTO**: 15 minutes  
**RPO**: 5 minutes  

---

## On-Call Procedures

### Initial Response (First 5 Minutes)

1. **Acknowledge alert** in PagerDuty/your monitoring system
2. **Check dashboard**: https://portal.azure.com/aria-prod
3. **Review logs**: Application Insights → Failed Requests
4. **Verify health**: `curl https://aria-prod.azurewebsites.net/api/ai/status`
5. **Start investigation** using full-stack debugging procedures below

### Escalation Path

```
Tier 1 (You) → 5 min
  ├─ Restart Function App
  ├─ Check provider connectivity
  └─ Review recent errors
       ↓
Tier 2 (Senior Dev) → 10 min
  ├─ Database issue diagnosis
  ├─ Provider failover
  └─ Performance analysis
       ↓
Tier 3 (Architecture) → 15 min
  ├─ Rollback decision
  ├─ Multi-region failover
  └─ Post-incident coordination
```

---

## Daily Operations Checklist

### Morning (First Thing)

```bash
# 1. Check system health
curl -s https://aria-prod.azurewebsites.net/api/ai/status | jq '.'

# 2. Check error rate in Application Insights
az monitor metrics show \
  --resource /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Insights/components/aria-prod-insights \
  --metric FailedRequests \
  --aggregation Total \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --interval PT1H

# 3. Check training cycles
curl -s https://aria-prod.azurewebsites.net/api/ai/status | jq '.orchestrators'

# 4. Verify database connectivity
# (Check in Azure Portal → SQL Database → Query Editor)
```

### Weekly

- [ ] Review Application Insights metrics for trends
- [ ] Check Azure Cost Management for unexpected charges
- [ ] Verify database backups completed successfully
- [ ] Test disaster recovery procedure (in staging environment)
- [ ] Review logs for any warnings or errors
- [ ] Verify all monitoring alerts are firing correctly

### Monthly

- [ ] Capacity planning: Analyze function execution time and resource usage
- [ ] Security audit: Review Key Vault expiration, role assignments, network rules
- [ ] Performance optimization: Identify slow queries, high-latency endpoints
- [ ] Update dependencies: Review and test security patches
- [ ] Disaster recovery drill: Full failover test to secondary region (if configured)
- [ ] Post-incident reviews: Discuss any issues from the past month

---

## Common Issues & Solutions

### Issue: Health Endpoint Returning 500

**Symptoms**: `/api/ai/status` returns HTTP 500

**Diagnosis**:
```bash
# Check Function App logs
az functionapp log tail \
  --name aria-prod \
  --resource-group aria-prod

# Check Application Insights
az monitor app-insights query \
  --app aria-insights \
  --resource-group aria-prod \
  --query "requests | where resultCode == '500' | project timeGenerated, name, resultCode, message"
```

**Common Causes & Fixes**:

1. **Provider detection failed**
   - Check Ollama connectivity: `curl http://ollama-service:11434/api/tags`
   - Verify OLLAMA_BASE_URL and OLLAMA_MODEL in settings
   - Fix: `az functionapp config appsettings set --name aria-prod --settings OLLAMA_MODEL=qwen2.5-coder:7b`

2. **Database connection pooled out**
   - Check pool saturation: Look for "Connection pool exhausted" in logs
   - Fix: Increase QAI_SQL_POOL_SIZE: `az functionapp config appsettings set --settings QAI_SQL_POOL_SIZE=30`
   - Or restart Function App: `az functionapp stop/start`

3. **Cosmos DB unavailable**
   - Check Cosmos status: `az cosmosdb show --name aria-prod-cosmos`
   - Disable if not needed: `az functionapp config appsettings set --settings QAI_ENABLE_COSMOS=false`

**Recovery**:
```bash
# Restart Function App
az functionapp stop --name aria-prod --resource-group aria-prod
sleep 30
az functionapp start --name aria-prod --resource-group aria-prod

# Verify recovery
curl https://aria-prod.azurewebsites.net/api/ai/status
```

---

### Issue: Chat Responses Timing Out

**Symptoms**: Chat requests take >30 seconds or timeout

**Diagnosis**:
```bash
# Check provider connectivity
curl http://ollama-service:11434/api/generate \
  -X POST \
  -d '{"model":"qwen2.5-coder:7b","prompt":"test"}'

# Monitor Function App performance
az monitor metrics show \
  --resource /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Web/sites/aria-prod \
  --metric FunctionExecutionUnits \
  --aggregation Average \
  --interval PT1M
```

**Common Causes & Fixes**:

1. **Ollama overloaded**
   - Check Ollama status: `curl http://ollama-service:11434/api/tags`
   - Reduce concurrent requests or scale Ollama service
   - Or switch provider to Azure OpenAI if available

2. **Function App hitting execution limits**
   - Check if running near timeout (30 sec default)
   - Increase timeout in host.json: `"functionTimeout": "00:05:00"`
   - Or optimize chat completion logic

3. **Network latency**
   - Check function-to-ollama latency: `ping ollama-service`
   - Verify network routing and firewall rules
   - Consider moving to same region/vnet

**Recovery**:
```bash
# If Ollama is stuck, restart it
# (assumes Ollama runs as a service)
systemctl restart ollama

# Or switch to local fallback temporarily
az functionapp config appsettings set \
  --settings DEFAULT_AI_PROVIDER=local
```

---

### Issue: High Error Rate (>1%)

**Symptoms**: Application Insights showing many failed requests

**Diagnosis**:
```bash
# Get error breakdown
az monitor app-insights query \
  --app aria-insights \
  --resource-group aria-prod \
  --query "requests | where resultCode >= '400' | summarize count() by resultCode, name"

# Check error details
az monitor app-insights query \
  --app aria-insights \
  --resource-group aria-prod \
  --query "requests | where resultCode >= '400' | top 10 by timeGenerated | project timeGenerated, name, resultCode, message, details"
```

**Common Causes**:

1. **Provider-specific errors** (most common)
   - Check `_looks_like_provider_error()` in gradio_hello.py
   - Review provider detection chain in shared/chat_providers.py
   - Fall back to local echo on Ollama failures

2. **Invalid input validation**
   - Requests with malformed JSON
   - Fix: Review request_validator.py schema

3. **Rate limiting** (if enabled)
   - Too many requests from single client
   - Check rate limiter config in function_app.py

**Recovery**:
```bash
# If provider is causing errors, disable it
az functionapp config appsettings set \
  --settings DEFAULT_AI_PROVIDER=local

# Monitor error rate recovery
az monitor metrics show \
  --resource /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Insights/components/aria-insights \
  --metric customMetrics/request_error_rate \
  --aggregation Average \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --interval PT5M
```

---

## Performance Tuning

### Optimize Function Execution Time

```bash
# Analyze slowest endpoints
az monitor app-insights query \
  --app aria-insights \
  --resource-group aria-prod \
  --query "requests | summarize avg(duration) by name | order by avg_duration desc | top 10"

# Check if specific operations are slow
az monitor app-insights query \
  --query "customEvents | where name == 'chat_completion' | summarize avg(duration) by tostring(customDimensions.provider)"
```

**Common Optimizations**:

1. **Token pruning**: Aggressive pruning to stay under context window
2. **Caching**: Cache provider info and model metadata
3. **Connection pooling**: Increase SQL pool size during high load
4. **Async operations**: Offload heavy computations to background jobs

### Scale Function App

```bash
# For Elastic Premium plan, increase pre-warmed instances
az appservice plan update \
  --name aria-prod-plan \
  --resource-group aria-prod \
  --sku EP2 \
  --number-of-workers 2

# OR increase maximum elastic worker count
# Edit in portal or via:
az functionapp config set \
  --name aria-prod \
  --resource-group aria-prod \
  --maximum-elastic-worker-count 20
```

---

## Disaster Recovery

### Failover to Secondary Region

1. **Automated**: If multi-region is configured, Azure handles transparently
2. **Manual**: If needed:

```bash
# Create new resource group in secondary region
az group create --name aria-prod-dr --location westus

# Deploy infrastructure to secondary region
az deployment group create \
  --resource-group aria-prod-dr \
  --template-file .azure/main.bicep \
  --parameters @.azure/environments/prod.parameters.json

# Restore database from backup
# (Handled automatically with geo-replication)

# Update DNS/routing to point to secondary region
# (Update in your DNS provider or Azure Traffic Manager)
```

### Restore from Backup

```bash
# List available backups
az sql db list-backups \
  --server aria-prod-sql \
  --resource-group aria-prod \
  --database aria_prod

# Restore to point-in-time
az sql db restore \
  --dest-name aria_prod_restored \
  --name aria_prod \
  --resource-group aria-prod \
  --server aria-prod-sql \
  --time "2026-06-01T12:00:00Z"

# Swap restored DB with production
# (Requires downtime, plan accordingly)
```

---

## Capacity Planning

### Monitor Resource Usage

```bash
# CPU usage over time
az monitor metrics show \
  --resource /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Web/serverfarms/aria-prod-plan \
  --metric CpuPercentage \
  --aggregation Average \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --interval P1D

# Memory usage
az monitor metrics show \
  --resource /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Web/serverfarms/aria-prod-plan \
  --metric MemoryPercentage \
  --aggregation Average
```

### Scaling Recommendations

- **CPU >80% sustained**: Increase plan tier or instance count
- **Memory >85% sustained**: Optimize code or add more memory
- **Database DTU >75%**: Upgrade SQL tier or add replicas
- **API latency >5s**: Profile slow paths or scale horizontally

---

## Security Incident Response

### If Breach is Suspected

1. **Isolate**: Take Function App offline if necessary
   ```bash
   az functionapp stop --name aria-prod --resource-group aria-prod
   ```

2. **Investigate**: Collect logs and evidence
   ```bash
   az functionapp log download --name aria-prod --resource-group aria-prod
   ```

3. **Rotate Credentials**:
   ```bash
   # Regenerate SQL password
   az sql server ad-admin create --resource-group aria-prod --server aria-prod-sql
   
   # Rotate Key Vault secrets
   az keyvault secret set --vault-name aria-prod-kv --name sql-password --value $(openssl rand -base64 32)
   ```

4. **Notify**: Escalate to security team immediately

5. **Remediate & Verify**:
   ```bash
   az functionapp start --name aria-prod --resource-group aria-prod
   # Run full verification suite
   .azure/verify-deployment.sh https://aria-prod.azurewebsites.net
   ```

---

## Monitoring Alerts Setup

```bash
# Alert: High error rate
az monitor metrics alert create \
  --name aria-high-error-rate \
  --resource-group aria-prod \
  --scopes /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Insights/components/aria-insights \
  --condition "total requests | where resultCode >= '500' > 10 in last 5m" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email --email-receiver <your-email>

# Alert: Function execution time
az monitor metrics alert create \
  --name aria-slow-execution \
  --resource-group aria-prod \
  --scopes /subscriptions/<SUB>/resourceGroups/aria-prod/providers/Microsoft.Web/sites/aria-prod \
  --condition "avg FunctionExecutionUnits > 1000000000" \
  --window-size 5m \
  --evaluation-frequency 1m
```

---

## Contact & Escalation

| Role | Contact | Availability |
|------|---------|--------------|
| On-Call Engineer | #oncall Slack | 24/7 |
| Platform Lead | — | Business hours |
| Architecture | — | Business hours + on-call |
| Incident Commander | — | During incidents |

**Escalation**: After 15 minutes with no resolution, escalate to next tier.

---

## Post-Incident Review Process

After any production incident:

1. **Timeline**: Document what happened and when
2. **Root Cause**: Why did it happen?
3. **Impact**: How many users affected? Duration?
4. **Resolution**: What fixed it?
5. **Prevention**: How do we prevent recurrence?
6. **Actions**: Assign owners for prevention items
7. **Communication**: Notify affected users

---

## Additional Resources

- **Architecture**: See `/workspaces/Aria/.github/copilot-instructions.md`
- **API Docs**: See `TOOLS.md` and endpoint definitions in `function_app.py`
- **Troubleshooting**: Check `.github/instructions/` for component-specific guidance
- **Skills**: Use `.github/skills/` for domain-specific procedures

---

**Last Updated**: June 1, 2026  
**Version**: 1.0.0  
**Status**: Production-Ready
