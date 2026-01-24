#!/usr/bin/env python
"""
Troubleshooting Guide & Diagnostic Runner
==========================================

Automated diagnostics for common issues in the QAI workspace.
Identifies problems and suggests solutions.

Usage:
    python scripts/monitoring/troubleshoot.py              # Run all diagnostics
    python scripts/monitoring/troubleshoot.py --diagnose <issue>  # Specific issue
    python scripts/monitoring/troubleshoot.py --fix <issue>      # Auto-fix (if available)
    python scripts/monitoring/troubleshoot.py --list             # List all issues
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# ANSI Colors
class C:
    H = '\033[95m'  # Header
    B = '\033[94m'  # Blue
    C = '\033[96m'  # Cyan
    G = '\033[92m'  # Green
    Y = '\033[93m'  # Yellow
    R = '\033[91m'  # Red
    X = '\033[0m'   # End
    BD = '\033[1m'  # Bold
    UL = '\033[4m'  # Underline

def fmt(text: str, color: str = C.X) -> str:
    return f"{color}{text}{C.X}"

# Diagnostic functions
class Diagnostics:
    
    @staticmethod
    def diagnose_provider_detection() -> Tuple[str, List[str]]:
        """Check chat provider detection issues"""
        issues = []
        
        try:
            from shared.chat_providers import detect_provider
            provider = detect_provider()
            
            findings = f"{fmt('Provider Detection Status', C.BD)}\n"
            findings += f"  Current provider: {fmt(provider, C.G)}\n"
            
            # Check each provider
            import os
            
            # Azure OpenAI
            azure_vars = [
                'AZURE_OPENAI_API_KEY',
                'AZURE_OPENAI_ENDPOINT',
                'AZURE_OPENAI_DEPLOYMENT',
                'AZURE_OPENAI_API_VERSION'
            ]
            azure_ok = all(os.getenv(v) for v in azure_vars)
            if not azure_ok:
                missing = [v for v in azure_vars if not os.getenv(v)]
                issues.append(f"Azure OpenAI: Missing {', '.join(missing)}")
                findings += f"  Azure: {fmt('✗', C.Y)} Missing: {', '.join(missing[:2])}...\n"
            else:
                findings += f"  Azure: {fmt('✓', C.G)}\n"
            
            # OpenAI
            openai_ok = bool(os.getenv('OPENAI_API_KEY'))
            findings += f"  OpenAI: {fmt('✓', C.G) if openai_ok else fmt('✗', C.Y)}\n"
            if not openai_ok:
                issues.append("OpenAI: OPENAI_API_KEY not set")
            
            # LMStudio
            lm_ok = bool(os.getenv('LMSTUDIO_BASE_URL'))
            findings += f"  LMStudio: {fmt('✓', C.G) if lm_ok else fmt('✗', C.Y)}\n"
            if not lm_ok:
                issues.append("LMStudio: LMSTUDIO_BASE_URL not set")
            
            if not issues:
                findings += f"\n  {fmt('✓ At least one provider is configured', C.G)}\n"
            
            return findings, issues
            
        except Exception as e:
            return f"{fmt('Error checking providers:', C.R)} {e}", [str(e)]
    
    @staticmethod
    def diagnose_training_stuck() -> Tuple[str, List[str]]:
        """Detect if training is stuck or hung"""
        issues = []
        
        findings = f"{fmt('Training Status', C.BD)}\n"
        
        status_file = REPO_ROOT / "data_out" / "autotrain" / "status.json"
        if not status_file.exists():
            findings += f"  {fmt('No training status found', C.Y)}\n"
            return findings, []
        
        try:
            with open(status_file) as f:
                data = json.load(f)
            
            status = data.get('status', 'unknown')
            timestamp_str = data.get('timestamp', '')
            
            findings += f"  Status: {fmt(status, C.G if status == 'completed' else C.Y)}\n"
            findings += f"  Last update: {timestamp_str}\n"
            
            if status == 'running':
                try:
                    last_update = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    elapsed = datetime.now(last_update.tzinfo) - last_update
                    
                    findings += f"  Elapsed: {elapsed}\n"
                    
                    if elapsed > timedelta(hours=2):
                        issues.append(f"Training running for {elapsed} (>2 hours)")
                        findings += f"  {fmt('⚠ Training appears stuck', C.R)}\n"
                        findings += f"     Consider checking logs or restarting\n"
                    elif elapsed > timedelta(hours=1):
                        findings += f"  {fmt('Running long', C.Y)} - monitor progress\n"
                except:
                    pass
            
            # Check for failed jobs
            jobs = data.get('jobs', {})
            failed_jobs = [name for name, job in jobs.items() if job.get('status') == 'failed']
            
            if failed_jobs:
                issues.append(f"Training has {len(failed_jobs)} failed job(s)")
                findings += f"  {fmt(f'Failed jobs: {len(failed_jobs)}', C.R)}\n"
                for job in failed_jobs[:3]:
                    findings += f"    • {job}\n"
            
        except Exception as e:
            findings += f"  {fmt('Error reading status:', C.R)} {e}\n"
            issues.append(str(e))
        
        return findings, issues
    
    @staticmethod
    def diagnose_disk_space() -> Tuple[str, List[str]]:
        """Check if disk space is running low"""
        issues = []
        
        findings = f"{fmt('Disk Space Status', C.BD)}\n"
        
        # Check data_out growth
        data_out = REPO_ROOT / "data_out"
        if data_out.exists():
            try:
                size = sum(f.stat().st_size for f in data_out.rglob("*") if f.is_file())
                size_gb = size / (1024**3)
                
                findings += f"  data_out: {fmt(f'{size_gb:.1f} GB', C.Y if size_gb > 50 else C.G)}\n"
                
                if size_gb > 100:
                    issues.append(f"data_out is {size_gb:.1f} GB (>100 GB)")
                    findings += f"    {fmt('Large - consider archiving old runs', C.Y)}\n"
                elif size_gb > 50:
                    findings += f"    {fmt('Moderate size - monitor growth', C.Y)}\n"
                    
            except Exception as e:
                findings += f"  Error: {e}\n"
        
        # Check models
        models_dir = REPO_ROOT / "deployed_models"
        if models_dir.exists():
            try:
                size = sum(f.stat().st_size for f in models_dir.rglob("*") if f.is_file())
                size_gb = size / (1024**3)
                findings += f"  deployed_models: {fmt(f'{size_gb:.1f} GB', C.Y if size_gb > 50 else C.G)}\n"
            except:
                pass
        
        findings += f"  {fmt('Tip:', C.BD)} Archive old runs: find data_out -name 'status.json' -mtime +30\n"
        
        return findings, issues
    
    @staticmethod
    def diagnose_api_connectivity() -> Tuple[str, List[str]]:
        """Check if Azure Functions and APIs are reachable"""
        issues = []
        
        findings = f"{fmt('API Connectivity', C.BD)}\n"
        
        endpoints = [
            ("Azure Functions", "http://localhost:7071/api/ai/status"),
            ("Chat API", "http://localhost:7071/api/chat"),
            ("Quantum Status", "http://localhost:7071/api/quantum/status"),
        ]
        
        try:
            import requests
            
            for name, url in endpoints:
                try:
                    resp = requests.get(url, timeout=2)
                    status = fmt('✓', C.G) if resp.ok else fmt('✗', C.Y)
                    findings += f"  {status} {name}: {resp.status_code}\n"
                    if not resp.ok:
                        issues.append(f"{name} returned {resp.status_code}")
                except requests.ConnectionError:
                    findings += f"  {fmt('✗', C.R)} {name}: Connection refused\n"
                    issues.append(f"{name}: Connection refused (is function app running?)")
                except requests.Timeout:
                    findings += f"  {fmt('✗', C.Y)} {name}: Timeout\n"
                    issues.append(f"{name}: Timeout (function app may be slow)")
                except Exception as e:
                    findings += f"  {fmt('✗', C.R)} {name}: {str(e)[:40]}\n"
                    issues.append(f"{name}: {e}")
        
        except ImportError:
            findings += f"  {fmt('requests library not installed', C.Y)}\n"
            issues.append("requests library not found (pip install requests)")
        
        findings += f"  {fmt('Tip:', C.BD)} Start function app with: func host start\n"
        
        return findings, issues
    
    @staticmethod
    def diagnose_database_health() -> Tuple[str, List[str]]:
        """Check database connectivity and health"""
        issues = []
        
        findings = f"{fmt('Database Health', C.BD)}\n"
        
        try:
            from shared.sql_engine import get_engine
            
            engine = get_engine()
            
            try:
                with engine.connect() as conn:
                    result = conn.execute('SELECT 1')
                    findings += f"  {fmt('✓', C.G)} SQL connection OK\n"
            except Exception as e:
                findings += f"  {fmt('✗', C.R)} SQL error: {str(e)[:50]}\n"
                issues.append(f"Database connection failed: {e}")
        
        except ImportError:
            findings += f"  {fmt('⚠', C.Y)} Could not import sql_engine\n"
        except Exception as e:
            findings += f"  {fmt('Error:', C.R)} {e}\n"
            issues.append(str(e))
        
        return findings, issues
    
    @staticmethod
    def diagnose_recent_errors() -> Tuple[str, List[str]]:
        """Check for recent errors in logs"""
        issues = []
        
        findings = f"{fmt('Recent Errors in Logs', C.BD)}\n"
        
        data_out = REPO_ROOT / "data_out"
        if not data_out.exists():
            findings += f"  {fmt('No logs found', C.Y)}\n"
            return findings, []
        
        error_count = 0
        error_by_dir = {}
        
        for log_file in data_out.glob("**/*.log"):
            try:
                with open(log_file) as f:
                    for line in f:
                        if 'error' in line.lower() or 'failed' in line.lower():
                            dir_name = log_file.parent.name
                            error_by_dir[dir_name] = error_by_dir.get(dir_name, 0) + 1
                            error_count += 1
            except:
                pass
        
        if error_count > 0:
            findings += f"  {fmt(f'{error_count}', C.R)} errors found\n"
            
            for dir_name, count in sorted(error_by_dir.items(), key=lambda x: x[1], reverse=True)[:5]:
                findings += f"    {dir_name}: {count}\n"
                if count > 10:
                    issues.append(f"{dir_name} has {count} errors")
        else:
            findings += f"  {fmt('✓ No errors found', C.G)}\n"
        
        return findings, issues
    
    @staticmethod
    def diagnose_orchestrator_hang() -> Tuple[str, List[str]]:
        """Detect if any orchestrator is hung/stuck"""
        issues = []
        
        findings = f"{fmt('Orchestrator Status', C.BD)}\n"
        
        data_out = REPO_ROOT / "data_out"
        if not data_out.exists():
            findings += f"  No status files found\n"
            return findings, []
        
        stuck_ops = []
        
        for status_file in data_out.glob("*/status.json"):
            try:
                with open(status_file) as f:
                    data = json.load(f)
                
                op_name = status_file.parent.name
                status = data.get('status', 'unknown')
                timestamp_str = data.get('timestamp', '')
                
                if status == 'running':
                    try:
                        last_update = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        elapsed = datetime.now(last_update.tzinfo) - last_update
                        
                        if elapsed > timedelta(hours=3):
                            stuck_ops.append((op_name, elapsed))
                            findings += f"  {fmt('✗', C.R)} {op_name}: STUCK for {elapsed}\n"
                        elif elapsed > timedelta(hours=1):
                            findings += f"  {fmt('⚠', C.Y)} {op_name}: running {elapsed}\n"
                    except:
                        findings += f"  {op_name}: {status}\n"
                else:
                    findings += f"  {fmt('✓', C.G)} {op_name}: {status}\n"
            
            except Exception as e:
                findings += f"  Error reading {status_file.name}: {e}\n"
        
        if stuck_ops:
            issues.append(f"{len(stuck_ops)} orchestrator(s) stuck")
            findings += f"\n  {fmt('Recovery:', C.BD)}\n"
            findings += f"    1. Check logs: tail -f data_out/<op_name>/*.log\n"
            findings += f"    2. Kill process: pkill -f <op_name>\n"
            findings += f"    3. Reset status: edit data_out/<op_name>/status.json\n"
        
        return findings, issues


# Issue definitions
ISSUES: List[Dict] = [
    {
        'id': 'provider',
        'title': 'Chat Provider Detection Issues',
        'diagnose': Diagnostics.diagnose_provider_detection,
        'fix': None,  # Manual fix required
    },
    {
        'id': 'training',
        'title': 'Training Appears Stuck',
        'diagnose': Diagnostics.diagnose_training_stuck,
        'fix': None,
    },
    {
        'id': 'disk',
        'title': 'Disk Space Issues',
        'diagnose': Diagnostics.diagnose_disk_space,
        'fix': None,
    },
    {
        'id': 'api',
        'title': 'API Connectivity Issues',
        'diagnose': Diagnostics.diagnose_api_connectivity,
        'fix': None,
    },
    {
        'id': 'db',
        'title': 'Database Connection Issues',
        'diagnose': Diagnostics.diagnose_database_health,
        'fix': None,
    },
    {
        'id': 'errors',
        'title': 'Recent Errors in Logs',
        'diagnose': Diagnostics.diagnose_recent_errors,
        'fix': None,
    },
    {
        'id': 'hang',
        'title': 'Orchestrator Hung/Stuck',
        'diagnose': Diagnostics.diagnose_orchestrator_hang,
        'fix': None,
    },
]

def run_diagnostics() -> None:
    """Run all diagnostics"""
    print(f"\n{fmt('╔════════════════════════════════════════╗', C.C)}")
    print(f"{fmt('║     QAI Workspace Diagnostics          ║', C.C)}")
    print(f"{fmt('╚════════════════════════════════════════╝', C.C)}\n")
    
    all_issues = []
    
    for issue in ISSUES:
        print(f"\n{fmt(issue['title'], C.BD)}")
        print("-" * 50)
        
        try:
            findings, issues = issue['diagnose']()
            print(findings)
            
            if issues:
                all_issues.extend(issues)
                print(f"{fmt('Issues found:', C.R)}")
                for issue_desc in issues:
                    print(f"  • {issue_desc}")
        
        except Exception as e:
            print(f"{fmt('Error:', C.R)} {e}")
    
    # Summary
    print(f"\n{fmt('═' * 50, C.C)}")
    print(f"{fmt('Summary', C.BD)}")
    print(f"{fmt('═' * 50, C.C)}\n")
    
    if all_issues:
        print(f"{fmt(f'⚠ Found {len(all_issues)} issue(s):', C.R)}\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        
        print(f"\n{fmt('Next steps:', C.BD)}")
        print(f"  1. Review the diagnostics above")
        print(f"  2. Check logs: tail -f data_out/*/stdout.log")
        print(f"  3. Run specific diagnostic: python scripts/monitoring/troubleshoot.py --diagnose <issue_id>")
    else:
        print(f"{fmt('✓ All systems operational!', C.G)}")
    
    print()

def list_issues() -> None:
    """List all available issues"""
    print(f"\n{fmt('Available Diagnostics:', C.C)}\n")
    
    for issue in ISSUES:
        print(f"  {fmt(issue['id'], C.BD)}: {issue['title']}")
    
    print()

def diagnose_issue(issue_id: str) -> None:
    """Run specific diagnostic"""
    issue = next((i for i in ISSUES if i['id'] == issue_id), None)
    
    if not issue:
        print(f"{fmt('Issue not found:', C.R)} {issue_id}")
        list_issues()
        return
    
    print(f"\n{fmt(issue['title'], C.BD)}")
    print("-" * 50)
    
    try:
        findings, issues = issue['diagnose']()
        print(findings)
        
        if issues:
            print(f"\n{fmt('Issues found:', C.R)}")
            for issue_desc in issues:
                print(f"  • {issue_desc}")
        else:
            print(f"\n{fmt('✓ No issues found', C.G)}")
    
    except Exception as e:
        print(f"{fmt('Error:', C.R)} {e}")
    
    print()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_issues()
        elif sys.argv[1] == '--diagnose' and len(sys.argv) > 2:
            diagnose_issue(sys.argv[2])
        elif sys.argv[1] == '--help':
            print(f"{__doc__}")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print(f"Use: python {sys.argv[0]} --help")
    else:
        run_diagnostics()

if __name__ == '__main__':
    main()
