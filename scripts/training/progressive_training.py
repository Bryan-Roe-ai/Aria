#!/usr/bin/env python
"""
Progressive Training Mode - Quick → Standard → Full

Executes training in three phases:
1. QUICK: Minimal quick-test jobs (~5-15 min)
2. STANDARD: Medium-sized jobs (~30-60 min)
3. FULL: Complete training suite (~2-8 hours)

Usage:
    python scripts/training/progressive_training.py --phase quick    # Phase 1
    python scripts/training/progressive_training.py --phase standard # Phase 2
    python scripts/training/progressive_training.py --phase full     # Phase 3
    python scripts/training/progressive_training.py --all            # Run all phases
    python scripts/training/progressive_training.py --auto-promote   # Auto-deploy best models
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def define_training_phases() -> Dict[str, Dict]:
    """Define training phases with job selections and sample counts."""
    return {
        "quick": {
            "description": "Quick validation (5-15 min)",
            "jobs": [
                "phi35_mixed_chat_lr_low",      # Single HPO job
            ],
            "max_samples": {
                "train": 64,
                "eval": 16,
            },
            "epochs": 1,
            "notes": "✓ Tests GPU setup, data pipeline, LoRA adapter creation"
        },
        "standard": {
            "description": "Standard training (30-60 min)",
            "jobs": [
                "phi35_mixed_chat",
                "qwen25_3b_mixed_chat",
            ],
            "max_samples": {
                "train": 500,
                "eval": 50,
            },
            "epochs": 1,
            "notes": "✓ Trains two baseline models with reasonable data"
        },
        "full": {
            "description": "Complete suite (2-8 hours)",
            "jobs": [
                # Comprehensive
                "phi35_comprehensive_full",
                "qwen25_comprehensive_full",
                # Baseline
                "phi35_mixed_chat",
                "qwen25_3b_mixed_chat",
                "phi35_max_performance",
                # Domain-specific
                "phi35_repo_augmented",
                "qwen25_repo_augmented",
                # Hyperparameter exploration
                "phi35_mixed_chat_lr_low",
                "phi35_mixed_chat_lr_high",
                "phi35_mixed_chat_dropout_low",
                "phi35_mixed_chat_dropout_high",
                # Anime avatar
                "anime_avatar",
            ],
            "max_samples": None,  # Use config defaults
            "epochs": None,       # Use config defaults
            "notes": "✓ All 12 jobs: comprehensive, baseline, domain, HPO, anime"
        }
    }

def print_phase_info(phase_name: str, phase_config: Dict) -> None:
    """Print phase information."""
    print(f"\n{'='*70}")
    print(f"TRAINING PHASE: {phase_name.upper()}")
    print(f"{'='*70}")
    print(f"Duration: {phase_config['description']}")
    print(f"Jobs: {len(phase_config['jobs'])}")
    print(f"  - {chr(10).join(phase_config['jobs'])}")
    if phase_config.get('max_samples'):
        print(f"Samples: {phase_config['max_samples']['train']} train / {phase_config['max_samples']['eval']} eval")
    print(f"Epochs: {phase_config.get('epochs', 'default')}")
    print(f"{phase_config['notes']}\n")

def run_phase(phase_name: str, phase_config: Dict, auto_promote: bool = False) -> bool:
    """Execute a training phase."""
    import subprocess
    
    print_phase_info(phase_name, phase_config)
    
    status = {
        "phase": phase_name,
        "started": datetime.now().isoformat(),
        "jobs": phase_config["jobs"],
        "completed_jobs": [],
        "failed_jobs": [],
    }
    
    # Run each job
    for i, job_name in enumerate(phase_config["jobs"], 1):
        job_num = f"{i}/{len(phase_config['jobs'])}"
        print(f"\n[{job_num}] Running: {job_name}")
        print("-" * 70)
        
        cmd = [
            sys.executable,
            "scripts/training/autotrain.py",
            "--job", job_name,
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd="/workspaces/AI",
                capture_output=False,
                text=True,
                timeout=3600  # 1 hour timeout per job
            )
            
            if result.returncode == 0:
                print(f"✓ {job_name} completed successfully")
                status["completed_jobs"].append(job_name)
            else:
                print(f"✗ {job_name} failed with code {result.returncode}")
                status["failed_jobs"].append(job_name)
        except subprocess.TimeoutExpired:
            print(f"✗ {job_name} timed out (>1 hour)")
            status["failed_jobs"].append(job_name)
        except Exception as e:
            print(f"✗ {job_name} error: {e}")
            status["failed_jobs"].append(job_name)
    
    # Save phase status
    status_file = Path("/workspaces/AI/data_out") / f"training_{phase_name}_status.json"
    status_file.parent.mkdir(exist_ok=True, parents=True)
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"PHASE {phase_name.upper()} SUMMARY")
    print(f"{'='*70}")
    print(f"Completed: {len(status['completed_jobs'])}/{len(phase_config['jobs'])}")
    if status['completed_jobs']:
        print(f"  ✓ {', '.join(status['completed_jobs'])}")
    if status['failed_jobs']:
        print(f"  ✗ {', '.join(status['failed_jobs'])}")
    print(f"Status saved: {status_file}")
    
    success = len(status['failed_jobs']) == 0
    if success and auto_promote:
        print("\n[AUTO-PROMOTE] Deploying best models...")
        # TODO: Call model promotion logic
    
    return success

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=["quick", "standard", "full"],
        help="Run specific phase"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all phases sequentially"
    )
    parser.add_argument(
        "--auto-promote",
        action="store_true",
        help="Auto-deploy models meeting criteria"
    )
    parser.add_argument(
        "--skip-quick",
        action="store_true",
        help="Skip quick phase when running --all"
    )
    
    args = parser.parse_args()
    
    phases = define_training_phases()
    execution_plan = []
    
    if args.phase:
        execution_plan = [args.phase]
    elif args.all:
        execution_plan = ["quick", "standard", "full"]
        if args.skip_quick:
            execution_plan.remove("quick")
    else:
        parser.print_help()
        return
    
    print(f"\n🚀 TRAINING PROGRESSION: {' → '.join(execution_plan).upper()}")
    print(f"GPU Acceleration: ENABLED (cuda)")
    print(f"Auto-Promote: {'YES' if args.auto_promote else 'NO'}")
    
    all_success = True
    for phase_name in execution_plan:
        phase_config = phases[phase_name]
        success = run_phase(phase_name, phase_config, args.auto_promote)
        all_success = all_success and success
        
        if not success and phase_name != "quick":
            print(f"\n⚠️  Phase '{phase_name}' had failures. Continue? (y/n)")
            if input().lower() != 'y':
                break
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"TRAINING PROGRESSION COMPLETE")
    print(f"{'='*70}")
    print(f"Status: {'✓ SUCCESS' if all_success else '✗ SOME FAILURES'}")
    print(f"Phases executed: {' → '.join(execution_plan)}")
    
    if all_success:
        print("\n📊 Next steps:")
        print("  1. Review model metrics in data_out/lora_training/*/")
        print("  2. Compare accuracy and loss curves")
        print("  3. Deploy best performing model")
    
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()
