# Azure Quantum Batch Job Automation Script
# Submits multiple QASM files to multiple hardware targets, monitors status/results, and logs job info

param(
    [string]$ResourceGroup = "rg-quantum-ai",
    [string]$WorkspaceName = "quantum-ai-workspace",
    [string]$Location = "eastus",
    [string[]]$QasmFiles = @("bell.qasm", "ghz.qasm"),
    [string[]]$Targets = @("ionq.qpu", "quantinuum.qpu")
)

function Info($msg) { Write-Host $msg -ForegroundColor Yellow }
function Ok($msg) { Write-Host $msg -ForegroundColor Green }
function Err($msg) { Write-Host $msg -ForegroundColor Red }

Write-Host "== Azure Quantum Batch Job Automation ==" -ForegroundColor Cyan

$JobLog = @()
foreach ($qasm in $QasmFiles) {
    foreach ($target in $Targets) {
        Info "Submitting $qasm to $target..."
        $job = az quantum job submit --resource-group $ResourceGroup --workspace-name $WorkspaceName --target-id $target --input-data $qasm --output json | ConvertFrom-Json
        if ($job -and $job.id) {
            Ok "Submitted job $($job.id) for $qasm on $target"
            $JobLog += [PSCustomObject]@{
                QasmFile = $qasm
                Target = $target
                JobId = $job.id
            }
        } else {
            Err "Failed to submit $qasm to $target"
        }
    }
}

# Monitor jobs
foreach ($entry in $JobLog) {
    Info "Monitoring job $($entry.JobId) ($($entry.QasmFile) on $($entry.Target))..."
    $status = az quantum job show --resource-group $ResourceGroup --workspace-name $WorkspaceName --job-id $entry.JobId --query "status" --output tsv
    Write-Host "  Status: $status"
    if ($status -eq "Succeeded") {
        $output = az quantum job output --resource-group $ResourceGroup --workspace-name $WorkspaceName --job-id $entry.JobId
        Write-Host "  Output: $output"
    }
}

Ok "Batch job automation complete. See above for job IDs and results."
