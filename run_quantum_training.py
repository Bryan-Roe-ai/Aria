#!/usr/bin/env python
"""
Quantum Training Execution Runner
Runs training jobs sequentially and captures metrics
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Setup paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "quantum" / "src"))

# Output log
OUTPUT_LOG = REPO_ROOT / "data_out" / "quantum_training_execution.log"
OUTPUT_LOG.parent.mkdir(parents=True, exist_ok=True)

def log_message(msg: str, also_print: bool = True):
    """Log message to both file and stdout"""
    if also_print:
        print(msg)
    with open(OUTPUT_LOG, "a") as f:
        f.write(msg + "\n")

def run_training(job_name: str, preset: str, epochs: int, batch_size: int, n_qubits: int):
    """Run a single training job and capture metrics"""
    import subprocess

    start_time = datetime.now()
    start_epoch = time.time()

    log_message(f"\n{'='*50}")
    log_message(f"Job: {job_name}")
    log_message(f"Preset: {preset} | Epochs: {epochs} | Batch: {batch_size} | QBits: {n_qubits}")
    log_message(f"Start: {start_time.isoformat()}")
    log_message(f"{'='*50}")

    cmd = [
        sys.executable,
        str(REPO_ROOT / "quantum" / "train_custom_dataset.py"),
        "--preset", preset,
        "--epochs", str(epochs),
        "--batch-size", str(batch_size),
        "--n-qubits", str(n_qubits),
    ]

    log_message(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=False,
            text=True,
            timeout=3600
        )

        end_epoch = time.time()
        end_time = datetime.now()
        duration = int(end_epoch - start_epoch)

        log_message(f"End: {end_time.isoformat()}")
        log_message(f"Duration: {duration}s ({duration//60}m {duration%60}s)")
        log_message(f"Exit Code: {result.returncode}")

        if result.returncode == 0:
            log_message(f"✅ SUCCESS: {job_name}")
            return True
        else:
            log_message(f"❌ FAILED: {job_name}")
            return False

    except subprocess.TimeoutExpired:
        log_message(f"❌ TIMEOUT: {job_name}")
        return False
    except Exception as e:
        log_message(f"❌ ERROR: {job_name} - {str(e)}")
        return False

def main():
    """Execute the training workflow"""
    # Clear previous log
    if OUTPUT_LOG.exists():
        OUTPUT_LOG.unlink()

    log_message(f"Quantum Training Workflow")
    log_message(f"Workspace: {REPO_ROOT}")
    log_message(f"Python: {sys.executable}")
    log_message(f"Start Time: {datetime.now().isoformat()}")

    results = {}

    # Step 1: Sanity test
    log_message("\n" + "="*50)
    log_message("STEP 1/3: Quick Sanity Test (Heart, 2 epochs)")
    log_message("="*50)
    results['sanity_test'] = run_training("sanity_test", "heart", 2, 16, 4)

    if not results['sanity_test']:
        log_message("\n❌ Sanity test failed. Aborting remaining jobs.")
        return 1

    # Step 2: Heart Quick
    log_message("\n" + "="*50)
    log_message("STEP 2/3: Heart Quick (50 epochs)")
    log_message("="*50)
    results['heart_quick'] = run_training("heart_quick", "heart", 50, 16, 4)

    # Step 3: Ionosphere Quick
    log_message("\n" + "="*50)
    log_message("STEP 3/3: Ionosphere Quick (100 epochs)")
    log_message("="*50)
    results['ionosphere_quick'] = run_training("ionosphere_quick", "ionosphere", 100, 16, 4)

    # Summary
    log_message("\n" + "="*50)
    log_message("TRAINING SUMMARY")
    log_message("="*50)

    summary = {
        'sanity_test': '✅ PASS' if results['sanity_test'] else '❌ FAIL',
        'heart_quick': '✅ PASS' if results['heart_quick'] else '❌ FAIL',
        'ionosphere_quick': '✅ PASS' if results['ionosphere_quick'] else '❌ FAIL',
    }

    for job, status in summary.items():
        log_message(f"{job}: {status}")

    log_message(f"\nOutput log: {OUTPUT_LOG}")
    log_message(f"Model artifacts: {REPO_ROOT / 'data_out' / 'quantum'}")

    # Check output directory
    output_dir = REPO_ROOT / "data_out" / "quantum"
    if output_dir.exists():
        log_message(f"\nContents of data_out/quantum/:")
        try:
            for item in sorted(output_dir.rglob("*")):
                if item.is_file():
                    size = item.stat().st_size
                    size_str = f"{size/1024/1024:.1f}MB" if size > 1024*1024 else f"{size/1024:.1f}KB"
                    rel_path = item.relative_to(REPO_ROOT)
                    log_message(f"  {rel_path} ({size_str})")
        except Exception as e:
            log_message(f"  Error listing: {e}")

    log_message("="*50)

    all_passed = all(results.values())
    if all_passed:
        log_message("\n✅ ALL JOBS COMPLETED SUCCESSFULLY")
        return 0
    else:
        log_message("\n❌ SOME JOBS FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
