#!/usr/bin/env python3
"""
Real-time Dataset Collection Monitor
Monitors all running collection processes and displays live statistics
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime


def count_datasets():
    """Count current datasets"""
    try:
        result = subprocess.run(
            ["find", "datasets", "-name", "*.csv", "-o", "-name", "*.jsonl"],
            capture_output=True,
            text=True,
            cwd="/workspaces/AI"
        )
        return len([line for line in result.stdout.strip().split('\n') if line])
    except:
        return 0


def get_running_collectors():
    """Get list of running collection processes"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        collectors = []
        for line in result.stdout.split('\n'):
            if 'python' in line and any(x in line for x in ['collector', 'dataset_automation']):
                if 'grep' not in line:
                    collectors.append(line)
        
        return collectors
    except:
        return []


def tail_log(logfile, lines=5):
    """Get last N lines from log file"""
    try:
        with open(logfile) as f:
            return ''.join(f.readlines()[-lines:])
    except:
        return "Log not available"


def main():
    """Main monitor loop"""
    log_dir = Path("/workspaces/AI/data_out/logs")
    
    print("="*80)
    print("📊 REAL-TIME DATASET COLLECTION MONITOR")
    print("="*80)
    print("Press Ctrl+C to stop monitoring\n")
    
    initial_count = count_datasets()
    start_time = datetime.now()
    
    try:
        while True:
            current_count = count_datasets()
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = (current_count - initial_count) / max(elapsed / 60, 1)
            
            print(f"\n{'='*80}")
            print(f"⏱️  Elapsed: {int(elapsed/60)}m {int(elapsed%60)}s")
            print(f"📊 Datasets: {current_count} (started with {initial_count})")
            print(f"📈 New: {current_count - initial_count}")
            print(f"🚀 Rate: {rate:.1f} datasets/min")
            print(f"{'='*80}")
            
            # Show running collectors
            collectors = get_running_collectors()
            if collectors:
                print(f"\n🔄 Running Collectors ({len(collectors)}):")
                for c in collectors:
                    parts = c.split()
                    if len(parts) > 10:
                        print(f"   • {' '.join(parts[10:13])}")
            else:
                print("\n✅ No collectors running")
            
            # Show log tails
            print(f"\n📝 Recent Activity:")
            
            if (log_dir / "huggingface.log").exists():
                print("\n   HuggingFace Collector:")
                lines = tail_log(log_dir / "huggingface.log", 2)
                for line in lines.strip().split('\n')[-2:]:
                    if line.strip():
                        print(f"   {line}")
            
            if (log_dir / "aggressive.log").exists():
                print("\n   Aggressive Collector:")
                lines = tail_log(log_dir / "aggressive.log", 2)
                for line in lines.strip().split('\n')[-2:]:
                    if line.strip():
                        print(f"   {line}")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print(f"\n\n{'='*80}")
        print("📊 FINAL STATISTICS")
        print(f"{'='*80}")
        print(f"Started with: {initial_count} datasets")
        print(f"Ended with: {current_count} datasets")
        print(f"Total added: {current_count - initial_count} datasets")
        print(f"Duration: {int(elapsed/60)}m {int(elapsed%60)}s")
        print(f"{'='*80}")


if __name__ == "__main__":
    main()
