from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run MCP validation suite: static config lint + stdio probe, "
            "and emit combined JSON."
        )
    )
    parser.add_argument(
        "--config",
        default=".vscode/mcp.json",
        help="Path to MCP config file.",
    )
    parser.add_argument(
        "--server",
        help="Validate only one server by name.",
    )
    parser.add_argument(
        "--output",
        default="data_out/mcp_validation_suite.json",
        help="Path to write combined JSON output.",
    )
    parser.add_argument(
        "--env-strict",
        action="store_true",
        help=(
            "Treat missing ${env:...} references as errors in both "
            "config-only and runtime phases."
        ),
    )
    return parser.parse_args()


def run_validator(
    python_exe: str,
    repo_root: Path,
    config: str,
    server: str | None,
    config_only: bool,
    env_strict: bool,
) -> tuple[int, dict[str, Any]]:
    cmd = [
        python_exe,
        "scripts/validate_mcp_setup.py",
        "--config",
        config,
        "--json",
    ]
    if config_only:
        cmd.append("--config-only")
    if env_strict:
        cmd.append("--env-strict")
    if server:
        cmd.extend(["--server", server])

    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )

    try:
        payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {
            "summary": {
                "total": 0,
                "ok": 0,
                "fail": 1,
                "all_ok": False,
            },
            "servers": [],
            "config_issues": [
                {
                    "code": "invalid_validator_output",
                    "detail": (
                        "Failed to parse JSON output from "
                        "validate_mcp_setup.py"
                    ),
                    "severity": "error",
                }
            ],
            "stderr": proc.stderr.strip(),
            "stdout": proc.stdout.strip(),
        }

    return proc.returncode, payload


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    python_exe = sys.executable
    config_code, config_payload = run_validator(
        python_exe=python_exe,
        repo_root=repo_root,
        config=args.config,
        server=args.server,
        config_only=True,
        env_strict=args.env_strict,
    )
    runtime_code, runtime_payload = run_validator(
        python_exe=python_exe,
        repo_root=repo_root,
        config=args.config,
        server=args.server,
        config_only=False,
        env_strict=args.env_strict,
    )

    all_ok = config_code == 0 and runtime_code == 0
    output_payload: dict[str, Any] = {
        "summary": {
            "all_ok": all_ok,
            "config_ok": config_code == 0,
            "runtime_ok": runtime_code == 0,
            "server": args.server,
            "config": args.config,
            "env_strict": args.env_strict,
        },
        "config_only": config_payload,
        "runtime_probe": runtime_payload,
    }

    out_path = (repo_root / args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")

    print(f"Wrote {out_path}")
    print(
        "suite_status="
        f"{'OK' if all_ok else 'FAIL'} "
        f"config_ok={config_code == 0} runtime_ok={runtime_code == 0}"
    )

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
