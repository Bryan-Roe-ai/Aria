# Monitoring & Debugging Examples

**Comprehensive guide with practical examples for monitoring, troubleshooting, and diagnosing QAI operations.**

Generated: January 2026

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Real-Time Monitoring](#real-time-monitoring)
3. [Training Debugging](#training-debugging)
4. [Quantum Operations Debugging](#quantum-operations-debugging)
5. [Chat Provider Issues](#chat-provider-issues)
6. [Performance & Resource Monitoring](#performance--resource-monitoring)
7. [Log Inspection Patterns](#log-inspection-patterns)
8. [Health Checks](#health-checks)
9. [Advanced Troubleshooting](#advanced-troubleshooting)

---

## Quick Diagnostics

### 1. System Health Overview
```bash
# Check complete system status in one command
python scripts/monitoring/auto_ops_dashboard.py

# Output shows:
# - All 10 orchestrators status
# - Job counts (total, running, failed, completed)
# - Success rates
# - CPU/memory/disk alerts
# - Last run times
```

### 2. Watch for Problems in Real-Time
```bash
# Auto-refresh every 5 seconds, highlight issues only
python scripts/monitoring/auto_ops_dashboard.py --problems

# Good for: Finding failures without noise
# Watch mode: Runs until Ctrl+C
```

### 3. Quick Setup Menu (Interactive)
```bash
# Interactive helper with 7 diagnostic options
python scripts/monitoring/vscode_quickstart.py

# Options:
# 1. Start Dashboard Server (web UI)
# 2. Start Alert Monitor (background alerts)
# 3. View CLI Dashboard (auto_ops_dashboard)
# 4. Show Help
# 5. Start Full Suite
# 6. Exit
```

---

## Real-Time Monitoring

### 1. Web Dashboard (Full UI)
```bash
# Start server on port 8765
python scripts/monitoring/vs_code_server.py

# Then access: http://localhost:8765
# Features:
# - Real-time metrics from all operations
# - Alert section at top
# - Pause/resume refresh
# - Dark/light theme toggle
# - JSON API endpoint: /api/status
```

### 2. Terminal Dashboard with Auto-Refresh
```bash
# Refresh every 5 seconds automatically
python scripts/monitoring/auto_ops_dashboard.py --watch

# Compact version (fewer details, more focus)
python scripts/monitoring/auto_ops_dashboard.py --watch --compact

# Watch only problems and alerts
python scripts/monitoring/auto_ops_dashboard.py --watch --problems
```

### 3. Export Status to JSON
```bash
# Get structured data for processing
python scripts/monitoring/auto_ops_dashboard.py --export

# Output format:
# {
#   "timestamp": "2026-01-24T10:30:00",
#   "summary": {...},
#   "operations": [
#     {"name": "autotrain", "status": "running", "jobs": {...}}
#   ]
# }

# Pipe to jq for filtering:
python scripts/monitoring/auto_ops_dashboard.py --export | jq '.operations[] | select(.status=="failed")'
```

---

## Training Debugging

### 1. Monitor AutoTrain Jobs
```bash
# Watch all training jobs in real-time
python scripts/monitoring/auto_ops_dashboard.py --watch

# Directly check AutoTrain status file
cat data_out/autotrain/status.json | python -m json.tool

# Expected structure:
# {
#   "operation": "autotrain",
#   "timestamp": "2026-01-24T10:30:00",
#   "status": "running",
#   "jobs": {...},
#   "completed_jobs": 3,
#   "failed_jobs": 0
# }
```

### 2. View Training Logs
```bash
# Stream the most recent training job
tail -f data_out/autotrain/job_*/stdout.log

# Last 50 lines of a specific job
tail -n 50 data_out/autotrain/job_phi35_chat/stdout.log

# Watch for errors
tail -f data_out/autotrain/job_*/stdout.log | grep -i "error\|cuda\|oom"

# Count errors in completed jobs
grep -r "error" data_out/autotrain/ --include="*.log" | wc -l
```

### 3. Check Training Config Issues
```bash
# Validate training YAML before running (dry-run)
python scripts/training/autotrain.py --dry-run

# Output shows:
# - Config parsed correctly
# - All datasets found
# - GPU availability
# - Estimated duration

# Check specific job config
cat config/training/autotrain.yaml | python -c "import sys, yaml; print(yaml.safe_load(sys.stdin)['jobs'][0])"
```

### 4. GGUF Training Monitoring
```bash
# Check GGUF training status
cat data_out/gguf_training/training_status.json | python -m json.tool

# View GGUF job progress
tail -f data_out/gguf_training/logs/*.log

# List all GGUF models generated
find data_out/gguf_training -name "*.gguf" -type f -exec ls -lh {} \;

# Validate GGUF model
python scripts/training/gguf_training_automation.py --validate data_out/gguf_training/model.gguf
```

### 5. Training Performance Analysis
```bash
# Check if training is memory-bound
python scripts/monitoring/resource_monitor.py --snapshot

# Output includes:
# - Current GPU memory usage
# - CPU utilization
# - Disk I/O
# - Memory pressure

# Watch memory during training
python scripts/monitoring/resource_monitor.py --stream  # Samples every 10s
```

---

## Quantum Operations Debugging

### 1. Monitor Quantum AutoRun
```bash
# Check quantum operation status
cat data_out/quantum_autorun/status.json | python -m json.tool

# Watch quantum jobs
python scripts/monitoring/auto_ops_dashboard.py --watch

# Filter for quantum only
python scripts/monitoring/auto_ops_dashboard.py --export | jq '.operations[] | select(.name=="quantum_autorun")'
```

### 2. Quantum Circuit Logs
```bash
# View quantum circuit execution logs
tail -f data_out/quantum_autorun/*.log

# Check for cost overruns
grep -i "cost\|estimate\|exceeded" data_out/quantum_autorun/*.log

# List all generated circuits
find data_out/quantum_autorun/circuits -name "*.json" | head -20

# Inspect circuit details
python -c "
import json
with open('data_out/quantum_autorun/circuits/circuit_001.json') as f:
    circuit = json.load(f)
    print(f'Qubits: {circuit.get(\"num_qubits\")}')
    print(f'Depth: {circuit.get(\"depth\")}')
    print(f'Operations: {len(circuit.get(\"operations\", []))}')
"
```

### 3. Validate Quantum Config
```bash
# Dry-run quantum jobs
python scripts/evaluation/quantum_autorun.py --dry-run

# Output shows:
# - Azure Quantum credentials valid
# - Quotas available
# - Cost estimate
# - Backends available

# Check quantum config
cat config/quantum/quantum_autorun.yaml
```

---

## Chat Provider Issues

### 1. Check Provider Status
```bash
# See which provider is active
curl http://localhost:7071/api/ai/status | python -m json.tool

# Output shows:
# {
#   "provider": "azure_openai",  # or "openai", "lmstudio", "local_echo"
#   "env_vars": {...},
#   "capabilities": {...}
# }

# Alternative: Direct Python check
python -c "
from shared.chat_providers import detect_provider
provider_info = detect_provider()
print(f'Active provider: {provider_info}')
"
```

### 2. Azure OpenAI Provider Debug
```bash
# Check if all required env vars are set
curl http://localhost:7071/api/ai/status | jq '.env_vars | {
  AZURE_OPENAI_API_KEY,
  AZURE_OPENAI_ENDPOINT,
  AZURE_OPENAI_DEPLOYMENT,
  AZURE_OPENAI_API_VERSION
}'

# Test Azure connectivity
python -c "
import os
from openai import AzureOpenAI

try:
    client = AzureOpenAI(
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
    )
    response = client.chat.completions.create(
        model=os.getenv('AZURE_OPENAI_DEPLOYMENT'),
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=10
    )
    print('✓ Azure OpenAI connection OK')
except Exception as e:
    print(f'✗ Error: {e}')
"
```

### 3. LMStudio Provider Debug
```bash
# Check if LMStudio is running
curl http://localhost:1234/v1/models 2>/dev/null || echo "✗ LMStudio not running"

# List available models
curl http://localhost:1234/v1/models | python -m json.tool

# Test inference
python -c "
import requests
response = requests.post(
    'http://localhost:1234/v1/chat/completions',
    json={
        'model': 'local-model',
        'messages': [{'role': 'user', 'content': 'test'}],
        'max_tokens': 10
    }
)
print('✓ LMStudio inference OK' if response.ok else f'✗ Error: {response.status_code}')
"
```

### 4. Chat Provider Fallback Chain
```bash
# Understand provider detection priority
python -c "
from shared.chat_providers import detect_provider
import os

print('Provider Detection Chain:')
print('1. Explicit flag (--provider)')
print('2. LMStudio:', 'AVAILABLE' if os.getenv('LMSTUDIO_BASE_URL') else 'Not configured')
print('3. Azure OpenAI:', 'AVAILABLE' if all([
    os.getenv('AZURE_OPENAI_API_KEY'),
    os.getenv('AZURE_OPENAI_ENDPOINT'),
    os.getenv('AZURE_OPENAI_DEPLOYMENT'),
    os.getenv('AZURE_OPENAI_API_VERSION')
]) else 'Missing env vars')
print('4. OpenAI:', 'AVAILABLE' if os.getenv('OPENAI_API_KEY') else 'Not configured')
print('5. LoRA adapter (--provider lora)')
print('6. Local echo (fallback)')
print()
print('Active provider:', detect_provider())
"
```

---

## Performance & Resource Monitoring

### 1. Real-Time Resource Usage
```bash
# Snapshot of current resources
python scripts/monitoring/resource_monitor.py --snapshot

# Output shows:
# - CPU utilization (overall and per-core)
# - Memory: used, free, percent
# - Disk: usage and free space
# - GPU: memory usage, temperature
# - Process counts

# Stream continuous monitoring (samples every 10 seconds)
python scripts/monitoring/resource_monitor.py --stream
```

### 2. GPU Memory Analysis
```bash
# Check GPU memory during training
nvidia-smi --loop-ms=1000  # Updates every second

# GPU memory by process
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader

# Monitor specific process
ps aux | grep python | grep train
nvidia-smi --pid <PID> --query-gpu=used_memory --format=csv,noheader
```

### 3. Disk Space Monitoring
```bash
# Check data_out growth
du -sh data_out/
du -sh data_out/*/ | sort -h | tail -10  # Top 10 largest

# Find large files
find data_out -type f -size +100M -exec ls -lh {} \; | awk '{print $5, $9}' | sort -h

# Archive old models
# Safety: verify before deleting
find data_out/autotrain -name "*.pt" -mtime +30 -type f  # Modified >30 days ago
```

### 4. Database Connection Pool
```bash
# Check SQL connection pool status
curl http://localhost:7071/api/ai/status | jq '.db_status'

# Output:
# {
#   "active_connections": 3,
#   "pool_size": 10,
#   "saturation_percent": 30,
#   "saturation_alert": false
# }

# Increase pool size if saturation >80%:
# Edit local.settings.json: "QAI_SQL_POOL_SIZE": 20
```

---

## Log Inspection Patterns

### 1. Find Errors Across Operations
```bash
# All errors from all operations
grep -r "error" data_out --include="*.log" | head -20

# Errors by operation
for dir in data_out/*/; do
  echo "=== $(basename $dir) ===" 
  grep -l "error" "$dir"*.log 2>/dev/null | xargs grep "error" 2>/dev/null | wc -l
done

# Recent errors (modified in last hour)
find data_out -name "*.log" -mmin -60 -exec grep -l "error" {} \;
```

### 2. Training Failure Analysis
```bash
# Check if training crashed
tail -20 data_out/autotrain/job_*/stdout.log

# CUDA errors
grep -i "cuda\|out of memory\|oom" data_out/autotrain/job_*/stdout.log

# Dataset errors
grep -i "dataset\|not found\|missing" data_out/autotrain/job_*/stdout.log

# Find failed jobs in status
cat data_out/autotrain/status.json | python -m json.tool | grep -A 5 '"status": "failed"'
```

### 3. Quantum Circuit Issues
```bash
# Check quantum validation errors
grep -i "validation\|failed\|invalid" data_out/quantum_autorun/*.log

# Cost estimation problems
grep -i "cost\|quota\|exceeded" data_out/quantum_autorun/*.log

# Connection issues
grep -i "azure\|connection\|timeout" data_out/quantum_autorun/*.log
```

### 4. Follow Log in Real-Time
```bash
# Current active operation
tail -f data_out/$(ls -t data_out/ | head -1)/*.log

# Multiple log streams simultaneously
tail -f data_out/autotrain/*.log data_out/quantum_autorun/*.log | grep --line-buffered "error\|completed\|finished"

# Colorize output
tail -f data_out/autotrain/*.log | sed 's/error/\x1b[31merror\x1b[0m/i'
```

---

## Health Checks

### 1. API Server Health
```bash
# Start Azure Functions locally
func host start

# In another terminal, check health
curl http://localhost:7071/api/ai/status | jq .

# Response indicates:
# - Active provider
# - All required env vars
# - DB connection pool status
# - GPU availability
# - Estimated costs if quantum
```

### 2. Comprehensive Setup Verification
```bash
# Check all dependencies and configs
python scripts/monitoring/verify_setup.py

# Checks:
# - Python version
# - Required packages
# - Environment variables
# - Data directories
# - Model files
# - Database connectivity
# - GPU drivers
# - Azure credentials
```

### 3. Database Health
```bash
# Monitor SQL health
python scripts/monitoring/sql_health_monitor.py

# Shows:
# - Connection pool status
# - Query latency
# - Error rates
# - Table stats

# Direct query check
python -c "
from shared.sql_engine import get_engine
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('✓ Database connected')
"
```

### 4. Function App Endpoints
```bash
# Check all API endpoints
for endpoint in /api/ai/status /api/chat /api/quantum/status; do
  echo "=== Testing $endpoint ==="
  curl -s http://localhost:7071$endpoint | head -c 200
  echo -e "\n"
done
```

---

## Advanced Troubleshooting

### 1. Orchestrator State Analysis
```bash
# View all orchestrator status files
for file in data_out/*/status.json; do
  echo "=== $(dirname $file) ==="
  cat $file | jq '{status: .status, timestamp: .timestamp, jobs: (.jobs | length)}'
done

# Find operations stuck longer than 1 hour
python -c "
import json
from datetime import datetime, timedelta
from pathlib import Path

now = datetime.now()
for status_file in Path('data_out').glob('*/status.json'):
    with open(status_file) as f:
        data = json.load(f)
        last_run = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        duration = now - last_run
        if duration > timedelta(hours=1) and data['status'] == 'running':
            print(f'STUCK: {status_file.parent.name} for {duration}')
"
```

### 2. Silent Failures Detection
```bash
# Operations marked as completed but with no success message
python -c "
import json
from pathlib import Path

for status_file in Path('data_out').glob('*/status.json'):
    with open(status_file) as f:
        data = json.load(f)
        if data.get('status') == 'completed':
            jobs = data.get('jobs', {})
            failed = sum(1 for j in jobs.values() if j.get('status') == 'failed')
            if failed > 0:
                print(f'{status_file.parent.name}: {failed} failed jobs in completed status')
"
```

### 3. Provider Chain Testing
```bash
# Test each provider in sequence
python -c "
import os
import sys

providers = [
    ('lmstudio', {'LMSTUDIO_BASE_URL': os.getenv('LMSTUDIO_BASE_URL')}),
    ('azure', {'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY')}),
    ('openai', {'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')}),
]

print('Testing provider availability:')
for name, required_vars in providers:
    available = all(required_vars.values())
    print(f'  {name}: {\"✓\" if available else \"✗\"}')
"
```

### 4. Clean Up Broken State
```bash
# Safely reset a stuck operation (dry-run first)
echo 'Stuck operations:' $(find data_out -name "status.json" -exec grep -l '"status": "running"' {} \;)

# Manual reset for a specific operation (DANGEROUS - do this carefully)
# 1. Stop the process: pkill -f orchestrator_name
# 2. Backup status: cp data_out/op_name/status.json data_out/op_name/status.json.backup
# 3. Edit status: sed -i 's/"status": "running"/"status": "stopped"/g' data_out/op_name/status.json
# 4. Verify: cat data_out/op_name/status.json | jq '.status'
```

---

## Quick Command Reference

```bash
# View everything
python scripts/monitoring/auto_ops_dashboard.py

# Watch for problems
python scripts/monitoring/auto_ops_dashboard.py --problems

# Web UI
python scripts/monitoring/vs_code_server.py

# Check resources
python scripts/monitoring/resource_monitor.py --snapshot

# Verify setup
python scripts/monitoring/verify_setup.py

# Check specific logs
tail -f data_out/*/stdout.log

# Recent errors
grep -r "error" data_out --include="*.log" | head -10

# Status JSON structure
cat data_out/autotrain/status.json | jq .
```

---

## Alert Severity Levels

| Level | Condition | Action |
|-------|-----------|--------|
| 🔴 Critical | CPU >95%, Memory >85%, Disk >85% | Immediate attention |
| 🟠 Error | Job failed, accuracy declined >10% | Check logs, restart |
| 🟡 Warning | CPU >80%, saturation >70% | Monitor, may need scaling |
| 🟢 OK | All metrics normal | No action needed |

---

## Integration with VS Code

### Task Shortcuts
- **Ctrl+Shift+P** → "Tasks: Run Task" → Select monitoring task
- Available tasks:
  - Monitor: Auto Ops Dashboard
  - Monitor: Auto Ops (Watch)
  - Monitor: Auto Ops (Problems Only)
  - Monitor: Dashboard Server (VS Code)
  - Monitor: Alert Monitor (Background)

### Output Panel
- View real-time monitoring output
- Search logs within panel
- Auto-scroll monitoring updates

---

*For the latest debugging patterns and monitoring updates, check `/workspaces/AI/scripts/monitoring/README.md`*
