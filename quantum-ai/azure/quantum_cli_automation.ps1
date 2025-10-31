# Azure Quantum CLI Automation Script
# Automates resource management and job lifecycle

param(
    [string]$ResourceGroup = "rg-quantum-ai",
    [string]$WorkspaceName = "quantum-ai-workspace",
    [string]$Location = "eastus"
)

function Info($msg) { Write-Host $msg -ForegroundColor Yellow }
function Ok($msg) { Write-Host $msg -ForegroundColor Green }
function Err($msg) { Write-Host $msg -ForegroundColor Red }

Write-Host "== Azure Quantum CLI Automation ==" -ForegroundColor Cyan

# 1. List available quantum targets
Info "Listing available quantum targets..."
az quantum target list --resource-group $ResourceGroup --workspace-name $WorkspaceName --location $Location

# 2. Submit a job (example: QASM file to IonQ hardware)
$QasmFile = "bell.qasm"  # Replace with your QASM file path
$TargetId = "ionq.qpu"   # Change to desired hardware target
Info "Submitting job to $TargetId..."
az quantum job submit --resource-group $ResourceGroup --workspace-name $WorkspaceName --target-id $TargetId --input-data $QasmFile

# 3. List jobs
Info "Listing recent jobs..."
az quantum job list --resource-group $ResourceGroup --workspace-name $WorkspaceName

# 4. Monitor job status/results
$JobId = Read-Host "Enter Job ID to monitor"
Info "Showing job status..."
az quantum job show --resource-group $ResourceGroup --workspace-name $WorkspaceName --job-id $JobId
Info "Retrieving job output..."
az quantum job output --resource-group $ResourceGroup --workspace-name $WorkspaceName --job-id $JobId

# 5. Resource group management (optional)
# Info "Creating resource group if needed..."
# az group create --name $ResourceGroup --location $Location

# 6. Workspace info
Info "Showing workspace info..."
az quantum workspace show --resource-group $ResourceGroup --workspace-name $WorkspaceName

Ok "Automation complete. Edit this script to customize targets, files, or add more steps!"
