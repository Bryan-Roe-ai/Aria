#!/usr/bin/env python
"""Direct quantum training execution via Python import"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Setup paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "quantum"))
sys.path.insert(0, str(REPO_ROOT / "quantum" / "src"))

# Ensure datasets directory exists
DATASETS_DIR = REPO_ROOT / "datasets" / "quantum"
OUTPUT_DIR = REPO_ROOT / "data_out" / "quantum"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = REPO_ROOT / "data_out" / "quantum_training_direct.log"

def log_msg(text: str):
    """Log to both stdout and file"""
    print(text)
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n")

def run_training_direct(name: str, preset: str, epochs: int, batch_size: int, n_qubits: int):
    """Run training by directly executing Python code"""
    try:
        log_msg(f"\n{'='*60}")
        log_msg(f"Job: {name}")
        log_msg(f"Config: preset={preset}, epochs={epochs}, batch_size={batch_size}, n_qubits={n_qubits}")
        
        start_time = datetime.now()
        start_sec = time.time()
        log_msg(f"Start Time: {start_time.isoformat()}")
        
        # Import the training module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "train_custom_dataset",
            REPO_ROOT / "quantum" / "train_custom_dataset.py"
        )
        train_module = importlib.util.module_from_spec(spec)
        
        # Set up argv to simulate CLI
        original_argv = sys.argv
        sys.argv = [
            "train_custom_dataset.py",
            "--preset", preset,
            "--epochs", str(epochs),
            "--batch-size", str(batch_size),
            "--n-qubits", str(n_qubits),
        ]
        
        try:
            # Execute the module
            spec.loader.exec_module(train_module)
            
            end_time = datetime.now()
            end_sec = time.time()
            duration = int(end_sec - start_sec)
            
            log_msg(f"End Time: {end_time.isoformat()}")
            log_msg(f"Duration: {duration}s ({duration//60}m {duration%60}s)")
            log_msg(f"✅ SUCCESS: {name}")
            
            # List generated files
            log_msg(f"Generated files in {OUTPUT_DIR}:")
            if OUTPUT_DIR.exists():
                for item in sorted(OUTPUT_DIR.rglob("*")):
                    if item.is_file():
                        size = item.stat().st_size
                        log_msg(f"  {item.relative_to(REPO_ROOT)}")
            
            return True
            
        except SystemExit as e:
            # The script calls sys.exit() which we need to catch
            if e.code in (0, None):
                log_msg(f"✅ SUCCESS: {name} (exit code: {e.code})")
                return True
            else:
                log_msg(f"❌ FAILED: {name} (exit code: {e.code})")
                return False
        finally:
            sys.argv = original_argv
    
    except Exception as e:
        log_msg(f"❌ ERROR in {name}: {type(e).__name__}: {str(e)}")
        import traceback
        log_msg(traceback.format_exc())
        return False

def main():
    """Main execution flow"""
    # Clear old log
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    
    log_msg("="*60)
    log_msg("QUANTUM TRAINING EXECUTION (DIRECT PYTHON)")
    log_msg("="*60)
    log_msg(f"Repo Root: {REPO_ROOT}")
    log_msg(f"Python: {sys.executable}")
    log_msg(f"Datasets: {DATASETS_DIR}")
    log_msg(f"Output: {OUTPUT_DIR}")
    log_msg(f"Start: {datetime.now().isoformat()}")
    
    results = {}
    
    # Step 1: Sanity Test
    log_msg("\n" + "-"*60)
    log_msg("STEP 1/3: SANITY TEST (Heart, 2 epochs)")
    log_msg("-"*60)
    results['sanity'] = run_training_direct("sanity_test", "heart", 2, 16, 4)
    
    if not results['sanity']:
        log_msg("\n⚠️  Sanity test failed. Aborting remaining jobs.")
        return 1
    
    # Step 2: Heart Quick
    log_msg("\n" + "-"*60)
    log_msg("STEP 2/3: HEART QUICK (50 epochs)")
    log_msg("-"*60)
    results['heart'] = run_training_direct("heart_quick", "heart", 50, 16, 4)
    
    # Step 3: Ionosphere Quick  
    log_msg("\n" + "-"*60)
    log_msg("STEP 3/3: IONOSPHERE QUICK (100 epochs)")
    log_msg("-"*60)
    results['ionosphere'] = run_training_direct("ionosphere_quick", "ionosphere", 100, 16, 4)
    
    # Final Summary
    log_msg("\n" + "="*60)
    log_msg("EXECUTION SUMMARY")
    log_msg("="*60)
    log_msg(f"Sanity Test: {'✅ PASS' if results['sanity'] else '❌ FAIL'}")
    log_msg(f"Heart Quick: {'✅ PASS' if results['heart'] else '❌ FAIL'}")
    log_msg(f"Ionosphere Quick: {'✅ PASS' if results['ionosphere'] else '❌ FAIL'}")
    
    log_msg(f"\nLog file: {LOG_FILE}")
    log_msg(f"Model outputs: {OUTPUT_DIR}")
    
    all_ok = all(results.values())
    if all_ok:
        log_msg("\n✅ ALL JOBS COMPLETED SUCCESSFULLY")
        return 0
    else:
        failed = [k for k,v in results.items() if not v]
        log_msg(f"\n❌ FAILED JOBS: {', '.join(failed)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
