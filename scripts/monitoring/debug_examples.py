#!/usr/bin/env python
"""
Interactive Monitoring & Debugging Examples
============================================

Real-world debugging scenarios with runnable examples.
Use this to quickly understand and test different monitoring capabilities.

Usage:
    python scripts/monitoring/debug_examples.py          # Interactive menu
    python scripts/monitoring/debug_examples.py --list   # List all examples
    python scripts/monitoring/debug_examples.py --run <example_id>  # Run specific example
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color(text: str, color_code: str) -> str:
    """Add ANSI color to text"""
    return f"{color_code}{text}{Colors.ENDC}"

# Example Functions
class DebugExamples:
    
    @staticmethod
    def example_check_provider_status() -> str:
        """Check which chat provider is currently active"""
        try:
            from shared.chat_providers import detect_provider
            
            result = f"""
{color('=== Chat Provider Status ===', Colors.CYAN)}

Current Provider:
"""
            provider = detect_provider()
            result += f"  {color('✓', Colors.GREEN)} Active: {provider}\n\n"
            
            result += "Environment Variables:\n"
            import os
            checks = {
                'Azure OpenAI': [
                    'AZURE_OPENAI_API_KEY',
                    'AZURE_OPENAI_ENDPOINT',
                    'AZURE_OPENAI_DEPLOYMENT',
                    'AZURE_OPENAI_API_VERSION'
                ],
                'OpenAI': ['OPENAI_API_KEY'],
                'LMStudio': ['LMSTUDIO_BASE_URL'],
            }
            
            for provider_name, vars_list in checks.items():
                status = "✓" if all(os.getenv(v) for v in vars_list) else "✗"
                color_code = Colors.GREEN if all(os.getenv(v) for v in vars_list) else Colors.YELLOW
                result += f"  {color(status, color_code)} {provider_name}\n"
                for var in vars_list:
                    val = os.getenv(var)
                    masked = f"[set]" if val else "[not set]"
                    result += f"      • {var}: {masked}\n"
            
            return result
            
        except Exception as e:
            return f"{color('Error:', Colors.RED)} {e}"
    
    @staticmethod
    def example_view_orchestrator_status() -> str:
        """View status of all orchestrators"""
        try:
            result = f"\n{color('=== Orchestrator Status ===', Colors.CYAN)}\n\n"
            
            data_out = REPO_ROOT / "data_out"
            if not data_out.exists():
                return f"{color('data_out/ directory not found', Colors.YELLOW)}"
            
            status_files = list(data_out.glob("*/status.json"))
            
            if not status_files:
                return f"{color('No status files found. Run an orchestrator first.', Colors.YELLOW)}"
            
            for status_file in sorted(status_files):
                try:
                    with open(status_file) as f:
                        data = json.load(f)
                    
                    op_name = status_file.parent.name
                    status = data.get('status', 'unknown')
                    timestamp = data.get('timestamp', 'unknown')
                    jobs_data = data.get('jobs', {})
                    
                    status_color = Colors.GREEN if status == 'completed' else Colors.YELLOW if status == 'running' else Colors.RED
                    
                    result += f"{color(op_name, Colors.BOLD)}\n"
                    result += f"  Status: {color(status, status_color)}\n"
                    result += f"  Last run: {timestamp}\n"
                    result += f"  Total jobs: {len(jobs_data)}\n"
                    
                    if jobs_data:
                        completed = sum(1 for j in jobs_data.values() if j.get('status') == 'completed')
                        failed = sum(1 for j in jobs_data.values() if j.get('status') == 'failed')
                        running = sum(1 for j in jobs_data.values() if j.get('status') == 'running')
                        
                        result += f"  Jobs: {color(str(completed), Colors.GREEN)} completed, "
                        result += f"{color(str(failed), Colors.RED) if failed > 0 else str(failed)} failed, "
                        result += f"{color(str(running), Colors.YELLOW) if running > 0 else str(running)} running\n"
                    
                    result += "\n"
                    
                except Exception as e:
                    result += f"  {color('Error reading:', Colors.RED)} {e}\n"
            
            return result
            
        except Exception as e:
            return f"{color('Error:', Colors.RED)} {e}"
    
    @staticmethod
    def example_find_recent_errors() -> str:
        """Find all recent errors in logs"""
        try:
            result = f"\n{color('=== Recent Errors ===', Colors.CYAN)}\n\n"
            
            data_out = REPO_ROOT / "data_out"
            if not data_out.exists():
                return f"{color('data_out/ directory not found', Colors.YELLOW)}"
            
            log_files = list(data_out.glob("**/*.log"))
            
            if not log_files:
                return f"{color('No log files found', Colors.YELLOW)}"
            
            errors_found = 0
            for log_file in sorted(log_files):
                try:
                    with open(log_file) as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        if 'error' in line.lower() or 'failed' in line.lower():
                            if errors_found == 0:
                                result += f"{color(str(log_file.relative_to(data_out)), Colors.BOLD)}\n"
                            result += f"  Line {i+1}: {line.strip()[:100]}\n"
                            errors_found += 1
                            if errors_found > 20:  # Limit output
                                break
                except:
                    pass
                
                if errors_found > 20:
                    result += f"\n{color('... (showing first 20 errors)', Colors.YELLOW)}\n"
                    break
            
            if errors_found == 0:
                result += f"{color('✓ No errors found', Colors.GREEN)}"
            
            return result
            
        except Exception as e:
            return f"{color('Error:', Colors.RED)} {e}"
    
    @staticmethod
    def example_check_disk_usage() -> str:
        """Check disk usage of data directories"""
        try:
            result = f"\n{color('=== Disk Usage ===', Colors.CYAN)}\n\n"
            
            dirs_to_check = [
                REPO_ROOT / "data_out",
                REPO_ROOT / "deployed_models",
                REPO_ROOT / "datasets",
            ]
            
            total_size = 0
            for dir_path in dirs_to_check:
                if dir_path.exists():
                    try:
                        size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())
                        total_size += size
                        size_gb = size / (1024**3)
                        
                        # Color code by size
                        if size_gb > 10:
                            color_code = Colors.RED
                        elif size_gb > 5:
                            color_code = Colors.YELLOW
                        else:
                            color_code = Colors.GREEN
                        
                        result += f"  {dir_path.name}: {color(f'{size_gb:.2f} GB', color_code)}\n"
                    except:
                        pass
            
            result += f"\n  Total: {color(f'{total_size / (1024**3):.2f} GB', Colors.BLUE)}\n"
            return result
            
        except Exception as e:
            return f"{color('Error:', Colors.RED)} {e}"
    
    @staticmethod
    def example_training_job_analysis() -> str:
        """Analyze training job success rates"""
        try:
            result = f"\n{color('=== Training Job Analysis ===', Colors.CYAN)}\n\n"
            
            status_file = REPO_ROOT / "data_out" / "autotrain" / "status.json"
            if not status_file.exists():
                return f"{color('AutoTrain status not found. Run training first.', Colors.YELLOW)}"
            
            with open(status_file) as f:
                data = json.load(f)
            
            jobs = data.get('jobs', {})
            if not jobs:
                return f"{color('No jobs found', Colors.YELLOW)}"
            
            result += f"Total jobs: {len(jobs)}\n"
            
            statuses = {}
            for job_name, job_data in jobs.items():
                status = job_data.get('status', 'unknown')
                statuses[status] = statuses.get(status, 0) + 1
                
                if status == 'completed':
                    success_rate = job_data.get('success_rate', 0)
                    result += f"\n  {color(job_name, Colors.BOLD)}\n"
                    result += f"    Status: {color('✓ Completed', Colors.GREEN)}\n"
                    result += f"    Success rate: {success_rate:.1f}%\n"
                elif status == 'failed':
                    result += f"\n  {color(job_name, Colors.BOLD)}\n"
                    result += f"    Status: {color('✗ Failed', Colors.RED)}\n"
                    error_msg = job_data.get('error', 'Unknown error')
                    result += f"    Error: {error_msg[:80]}\n"
            
            result += f"\n\nSummary:\n"
            for status, count in statuses.items():
                color_code = Colors.GREEN if status == 'completed' else Colors.RED if status == 'failed' else Colors.YELLOW
                result += f"  {color(status, color_code)}: {count}\n"
            
            return result
            
        except Exception as e:
            return f"{color('Error:', Colors.RED)} {e}"
    
    @staticmethod
    def example_quick_health_check() -> str:
        """Run a quick health check on all systems"""
        try:
            result = f"\n{color('=== Quick Health Check ===', Colors.CYAN)}\n\n"
            
            checks = []
            
            # Check data_out directory
            data_out = REPO_ROOT / "data_out"
            checks.append((
                "data_out directory",
                data_out.exists(),
                Colors.GREEN if data_out.exists() else Colors.RED
            ))
            
            # Check status files
            status_files = list(data_out.glob("*/status.json")) if data_out.exists() else []
            checks.append((
                f"Orchestrator status files ({len(status_files)})",
                len(status_files) > 0,
                Colors.GREEN if len(status_files) > 0 else Colors.YELLOW
            ))
            
            # Check Python dependencies
            try:
                import shared.chat_providers
                checks.append(("Chat providers module", True, Colors.GREEN))
            except:
                checks.append(("Chat providers module", False, Colors.RED))
            
            # Try Azure Functions endpoint
            try:
                import requests
                resp = requests.get("http://localhost:7071/api/ai/status", timeout=2)
                checks.append(("Azure Functions API", resp.ok, Colors.GREEN if resp.ok else Colors.YELLOW))
            except:
                checks.append(("Azure Functions API", False, Colors.YELLOW))
            
            # Check environment
            env_vars = ['AZURE_OPENAI_API_KEY', 'OPENAI_API_KEY', 'LMSTUDIO_BASE_URL']
            has_provider = any(os.getenv(var) for var in env_vars)
            checks.append((
                "Chat provider configured",
                has_provider,
                Colors.GREEN if has_provider else Colors.YELLOW
            ))
            
            for check_name, passed, color_code in checks:
                status_symbol = "✓" if passed else "✗"
                result += f"  {color(status_symbol, color_code)} {check_name}\n"
            
            return result
            
        except Exception as e:
            return f"{color('Error:', Colors.RED)} {e}"

# Example definitions
EXAMPLES: List[Dict[str, Any]] = [
    {
        'id': '1',
        'name': 'Check Chat Provider Status',
        'description': 'See which chat provider is active and check environment variables',
        'func': DebugExamples.example_check_provider_status,
    },
    {
        'id': '2',
        'name': 'View Orchestrator Status',
        'description': 'Check status of all running orchestrators',
        'func': DebugExamples.example_view_orchestrator_status,
    },
    {
        'id': '3',
        'name': 'Find Recent Errors',
        'description': 'Scan logs for recent errors and failures',
        'func': DebugExamples.example_find_recent_errors,
    },
    {
        'id': '4',
        'name': 'Check Disk Usage',
        'description': 'View disk usage of key directories',
        'func': DebugExamples.example_check_disk_usage,
    },
    {
        'id': '5',
        'name': 'Training Job Analysis',
        'description': 'Analyze training job success rates and errors',
        'func': DebugExamples.example_training_job_analysis,
    },
    {
        'id': '6',
        'name': 'Quick Health Check',
        'description': 'Run quick health checks on all systems',
        'func': DebugExamples.example_quick_health_check,
    },
]

def print_menu():
    """Print interactive menu"""
    print(f"\n{color('╔═══════════════════════════════════════════════════════════╗', Colors.CYAN)}")
    print(f"{color('║          Monitoring & Debugging Examples                  ║', Colors.CYAN)}")
    print(f"{color('╚═══════════════════════════════════════════════════════════╝', Colors.CYAN)}\n")
    
    for example in EXAMPLES:
        print(f"{color(example['id'], Colors.BOLD)}. {example['name']}")
        print(f"   {example['description']}")
    
    print(f"\n{color('Other commands:', Colors.BOLD)}")
    print(f"  {color('l', Colors.BOLD)}. List all examples")
    print(f"  {color('q', Colors.BOLD)}. Quit")
    print()

def run_example(example_id: str) -> None:
    """Run a specific example"""
    example = next((e for e in EXAMPLES if e['id'] == example_id), None)
    
    if not example:
        print(f"{color('Invalid example ID', Colors.RED)}")
        return
    
    name = example['name']
    print(f"\n{color(f'Running: {name}', Colors.BOLD)}")
    print("-" * 60)
    
    try:
        output = example['func']()
        print(output)
    except KeyboardInterrupt:
        print(f"\n{color('Interrupted', Colors.YELLOW)}")
    except Exception as e:
        print(f"{color('Error:', Colors.RED)} {e}")
    
    print("-" * 60)

def list_examples() -> None:
    """List all examples with details"""
    print(f"\n{color('Available Debugging Examples:', Colors.CYAN)}\n")
    
    for example in EXAMPLES:
        print(f"{color(f'[{example[\"id\"]}]', Colors.BOLD)} {example['name']}")
        print(f"     {example['description']}\n")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_examples()
        elif sys.argv[1] == '--run' and len(sys.argv) > 2:
            run_example(sys.argv[2])
        else:
            print(f"Usage: {sys.argv[0]} [--list | --run <example_id>]")
    else:
        # Interactive mode
        while True:
            print_menu()
            choice = input(f"{color('Choose an example (1-6, l, q): ', Colors.BOLD)}").strip().lower()
            
            if choice == 'q':
                print(f"{color('Goodbye!', Colors.CYAN)}")
                sys.exit(0)
            elif choice == 'l':
                list_examples()
            elif choice in [e['id'] for e in EXAMPLES]:
                run_example(choice)
                input(f"\n{color('Press Enter to continue...', Colors.YELLOW)}")
            else:
                print(f"{color('Invalid choice', Colors.RED)}")

if __name__ == '__main__':
    main()
