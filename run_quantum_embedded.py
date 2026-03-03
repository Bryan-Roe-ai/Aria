#!/usr/bin/env python
"""
Embedded Quantum Trainer - runs training inline without subprocess
Writes results to JSON files in data_out/quantum_training/
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
import io
import contextlib

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "quantum"))

OUTPUT_BASE = REPO_ROOT / "data_out" / "quantum_training"
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

SUMMARY_FILE = OUTPUT_BASE / "execution_summary.json"
LOG_FILE = OUTPUT_BASE / "execution.log"

def write_log(msg: str):
    """Write message to log file"""
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def run_training_embedded(job_name: str, preset: str, epochs: int, batch_size: int, n_qubits: int):
    """Run training by executing command with sys.argv modification"""
    try:
        write_log(f"\n{'='*60}")
        write_log(f"Job: {job_name}")
        write_log(f"Config: preset={preset}, epochs={epochs}, batch={batch_size}, qubits={n_qubits}")
        
        start_time = datetime.now()
        start_sec = time.time()
        write_log(f"Start: {start_time.isoformat()}")
        
        # Prepare argv for train_custom_dataset.py
        original_argv = sys.argv
        sys.argv = [
            str(REPO_ROOT / "quantum" / "train_custom_dataset.py"),
            "--preset", preset,
            "--epochs", str(epochs),
            "--batch-size", str(batch_size),
            "--n-qubits", str(n_qubits),
        ]
        
        output_buffer = io.StringIO()
        error_occurred = False
        error_msg = ""
        
        try:
            # Execute the training script by running its __main__
            with open(REPO_ROOT / "quantum" / "train_custom_dataset.py") as f:
                script_code = f.read()
            
            # Create a new namespace with necessary context
            namespace = {
                "__name__": "__main__",
                "__file__": str(REPO_ROOT / "quantum" / "train_custom_dataset.py"),
                "__doc__": "Training script execution",
            }
            
            # Capture output
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                try:
                    exec(script_code, namespace)
                except SystemExit as e:
                    if e.code not in (0, None):
                        error_occurred = True
                        error_msg = f"SystemExit: {e.code}"
                except Exception as e:
                    error_occurred = True
                    error_msg = f"{type(e).__name__}: {str(e)}"
            
            # Get captured output
            captured_output = output_buffer.getvalue()
            if captured_output:
                write_log(f"\nTraining output:\n{captured_output[-1000:]}")  # Last 1000 chars
            
            if error_occurred:
                write_log(f"❌ FAILED: {job_name} - {error_msg}")
                return {
                    "name": job_name,
                    "status": "failed",
                    "error": error_msg,
                    "duration": int(time.time() - start_sec)
                }
            
            end_time = datetime.now()
            duration = int(time.time() - start_sec)
            
            write_log(f"End: {end_time.isoformat()}")
            write_log(f"Duration: {duration}s ({duration//60}m {duration%60}s)")
            write_log(f"✅ SUCCESS: {job_name}")
            
            return {
                "name": job_name,
                "status": "success",
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration": duration,
                "preset": preset,
                "epochs": epochs,
            }
            
        finally:
            sys.argv = original_argv
    
    except Exception as e:
        write_log(f"❌ ERROR in {job_name}: {type(e).__name__}: {str(e)}")
        import traceback
        write_log(traceback.format_exc())
        return {
            "name": job_name,
            "status": "error",
            "error": str(e),
        }

def main():
    """Execute training workflow"""
    # Clear old log
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    
    write_log("="*60)
    write_log("QUANTUM TRAINING - EMBEDDED EXECUTOR")
    write_log("="*60)
    write_log(f"Repo: {REPO_ROOT}")
    write_log(f"Output: {OUTPUT_BASE}")
    write_log(f"Time: {datetime.now().isoformat()}")
    
    results = []
    
    # Step 1: Sanity test
    write_log("\n" + "-"*60)
    write_log("STEP 1/3: Sanity Test (heart, 2 epochs)")
    write_log("-"*60)
    r1 = run_training_embedded("sanity_test", "heart", 2, 16, 4)
    results.append(r1)
    
    if r1["status"] != "success":
        write_log("\n⚠️  Sanity test failed! Stopping execution.")
        summary = {
            "total": 1,
            "succeeded": 0,
            "failed": 1,
            "results": results,
        }
        SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
        return 1
    
    # Step 2: Heart quick
    write_log("\n" + "-"*60)
    write_log("STEP 2/3: Heart Quick (50 epochs)")
    write_log("-"*60)
    r2 = run_training_embedded("heart_quick", "heart", 50, 16, 4)
    results.append(r2)
    
    # Step 3: Ionosphere quick
    write_log("\n" + "-"*60)
    write_log("STEP 3/3: Ionosphere Quick (100 epochs)")
    write_log("-"*60)
    r3 = run_training_embedded("ionosphere_quick", "ionosphere", 100, 16, 4)
    results.append(r3)
    
    # Summary
    write_log("\n" + "="*60)
    write_log("EXECUTION SUMMARY")
    write_log("="*60)
    
    succeeded = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ("failed", "error"))
    
    for r in results:
        status_icon = "✅" if r["status"] == "success" else "❌"
        write_log(f"{status_icon} {r['name']}: {r['status']}")
        if r["status"] == "success" and "duration" in r:
            write_log(f"   Duration: {r['duration']}s")
    
    summary = {
        "total": len(results),
        "succeeded": succeeded,
        "failed": failed,
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }
    
    write_log(f"\nTotal: {summary['total']} | Success: {succeeded} | Failed: {failed}")
    write_log(f"Summary: {SUMMARY_FILE}")
    
    # Write summary to JSON
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2))
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
