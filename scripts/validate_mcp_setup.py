from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class ServerValidationResult:
    name: str
    ok: bool
    detail: str
    tool_names: list[str]


@dataclass
class LocalStdioServerParameters:
    command: str
    args: list[str]
    env: dict[str, str]
    cwd: str


INPUT_REF_RE = re.compile(r"\$\{input:([^}]+)\}")
ENV_REF_RE = re.compile(r"\$\{env:([^}]+)\}")


@dataclass
class ConfigValidationIssue:
    code: str
    detail: str
    severity: str = "error"


def has_error_issues(issues: list[ConfigValidationIssue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


def validate_config_inputs(
    config: dict[str, Any],
    only_server: str | None = None,
    env_strict: bool = False,
) -> list[ConfigValidationIssue]:
    issues: list[ConfigValidationIssue] = []
    inputs = config.get("inputs", [])
    servers = config.get("servers", {})

    defined_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    referenced_ids: set[str] = set()
    env_issues_seen: set[tuple[str, str, str]] = set()

    for item in inputs:
        if not isinstance(item, dict):
            continue
        input_id = item.get("id")
        if isinstance(input_id, str):
            if input_id in defined_ids:
                duplicate_ids.add(input_id)
            defined_ids.add(input_id)

    for dup_id in sorted(duplicate_ids):
        issues.append(
            ConfigValidationIssue(
                code="duplicate_input_id",
                detail=f"Duplicate input id: {dup_id}",
            )
        )

    if only_server and only_server not in servers:
        issues.append(
            ConfigValidationIssue(
                code="server_not_found",
                detail=(f"Requested server for config lint not found: {only_server}"),
            )
        )
        return issues

    for name, server in servers.items():
        if only_server and name != only_server:
            continue
        if not isinstance(server, dict):
            continue

        refs: list[tuple[str, str]] = []

        command = str(server.get("command", ""))
        refs.extend(("command", m.group(1)) for m in INPUT_REF_RE.finditer(command))

        for arg in server.get("args", []):
            arg_s = str(arg)
            refs.extend(("args", m.group(1)) for m in INPUT_REF_RE.finditer(arg_s))

        for k, v in server.get("env", {}).items():
            v_s = str(v)
            refs.extend((f"env.{k}", m.group(1)) for m in INPUT_REF_RE.finditer(v_s))

        for where, ref in refs:
            referenced_ids.add(ref)
            if ref not in defined_ids:
                issues.append(
                    ConfigValidationIssue(
                        code="undefined_input_reference",
                        detail=(f"Server '{name}' has undefined input reference '{ref}' in {where}"),
                    )
                )

        env_refs: list[tuple[str, str]] = []
        env_refs.extend(("command", m.group(1)) for m in ENV_REF_RE.finditer(command))
        for arg in server.get("args", []):
            arg_s = str(arg)
            env_refs.extend(("args", m.group(1)) for m in ENV_REF_RE.finditer(arg_s))
        for k, v in server.get("env", {}).items():
            v_s = str(v)
            env_refs.extend((f"env.{k}", m.group(1)) for m in ENV_REF_RE.finditer(v_s))

        for where, ref in env_refs:
            key = (name, where, ref)
            if key in env_issues_seen:
                continue
            env_issues_seen.add(key)
            if ref not in os.environ:
                issues.append(
                    ConfigValidationIssue(
                        code="missing_env_reference",
                        detail=(f"Server '{name}' references missing env var '{ref}' in {where}"),
                        severity="error" if env_strict else "warning",
                    )
                )

    if only_server is None:
        for input_id in sorted(defined_ids - referenced_ids):
            issues.append(
                ConfigValidationIssue(
                    code="unused_input_id",
                    detail=(f"Input id is defined but not referenced by any selected server: {input_id}"),
                    severity="warning",
                )
            )

    return issues


def strip_jsonc_comments(text: str) -> str:
    result: list[str] = []
    in_string = False
    escape = False
    index = 0

    while index < len(text):
        char = text[index]

        if in_string:
            result.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            result.append(char)
            index += 1
            continue

        if char == "/" and index + 1 < len(text) and text[index + 1] == "/":
            while index < len(text) and text[index] != "\n":
                index += 1
            continue

        result.append(char)
        index += 1

    return "".join(result)


def resolve_workspace_value(value: str, workspace: Path) -> str:
    return value.replace("${workspaceFolder}", str(workspace))


def load_mcp_config(config_path: Path) -> dict[str, Any]:
    text = config_path.read_text(encoding="utf-8")
    return json.loads(strip_jsonc_comments(text))


def build_server_params(
    workspace: Path,
    server_config: dict[str, Any],
) -> LocalStdioServerParameters:
    if "command" not in server_config:
        raise ValueError("Missing required 'command' for stdio server")

    command = resolve_workspace_value(server_config["command"], workspace)
    args = [resolve_workspace_value(arg, workspace) for arg in server_config.get("args", [])]
    env = {key: resolve_workspace_value(value, workspace) for key, value in server_config.get("env", {}).items()}
    cwd_raw = server_config.get("cwd", str(workspace))
    cwd = resolve_workspace_value(cwd_raw, workspace)
    return LocalStdioServerParameters(
        command=command,
        args=args,
        env=env,
        cwd=cwd,
    )


def format_exception_detail(exc: BaseException) -> str:
    nested = getattr(exc, "exceptions", None)
    if nested:
        first = nested[0]
        return f"{type(exc).__name__}: {first}"
    return str(exc)


def has_dynamic_substitutions(server_config: dict[str, Any]) -> bool:
    dynamic_markers = ("${input:", "${command:")

    command = str(server_config.get("command", ""))
    if any(marker in command for marker in dynamic_markers):
        return True

    for arg in server_config.get("args", []):
        if any(marker in str(arg) for marker in dynamic_markers):
            return True

    for value in server_config.get("env", {}).values():
        if any(marker in str(value) for marker in dynamic_markers):
            return True

    return False


async def validate_server(
    name: str,
    workspace: Path,
    server_config: dict[str, Any],
) -> ServerValidationResult:
    server_type = server_config.get("type", "stdio")

    if server_type != "stdio":
        return ServerValidationResult(
            name,
            True,
            f"SKIP: unsupported server type '{server_type}'",
            [],
        )

    command = str(server_config.get("command", ""))
    if has_dynamic_substitutions(server_config):
        return ServerValidationResult(
            name,
            True,
            "SKIP: server uses interactive/editor substitutions",
            [],
        )

    if command in {"docker", "npx", "uvx"}:
        return ServerValidationResult(
            name,
            True,
            (f"SKIP: external launcher '{command}' not validated in local stdio probe"),
            [],
        )

    try:
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
    except ImportError:
        return ServerValidationResult(
            name,
            False,
            "mcp package is not installed",
            [],
        )

    try:
        server_params = build_server_params(workspace, server_config)
        params = StdioServerParameters(
            command=server_params.command,
            args=server_params.args,
            env=server_params.env,
            cwd=server_params.cwd,
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                tool_names = [tool.name for tool in tools.tools]
                detail = f"{len(tool_names)} tools: {', '.join(tool_names)}"
                return ServerValidationResult(name, True, detail, tool_names)
    except Exception as exc:
        return ServerValidationResult(
            name,
            False,
            format_exception_detail(exc),
            [],
        )


async def validate_servers(
    workspace: Path,
    config_path: Path,
    only_server: str | None = None,
) -> list[ServerValidationResult]:
    config = load_mcp_config(config_path)
    servers = config.get("servers", {})
    results: list[ServerValidationResult] = []

    for name, server_config in servers.items():
        if only_server and name != only_server:
            continue
        results.append(await validate_server(name, workspace, server_config))

    return results


def results_to_json(results: list[ServerValidationResult]) -> dict[str, Any]:
    return {
        "summary": {
            "total": len(results),
            "ok": sum(1 for result in results if result.ok),
            "fail": sum(1 for result in results if not result.ok),
            "all_ok": all(result.ok for result in results),
        },
        "servers": [asdict(result) for result in results],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate stdio MCP servers configured in .vscode/mcp.json")
    parser.add_argument(
        "--config",
        default=".vscode/mcp.json",
        help="Path to MCP config file",
    )
    parser.add_argument(
        "--server",
        help="Validate only a single configured server by name",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON output instead of plain text",
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help=("Run only static MCP config checks (inputs/references), skip stdio probes"),
    )
    parser.add_argument(
        "--env-strict",
        action="store_true",
        help=("Treat missing ${env:...} references as errors instead of warnings"),
    )
    return parser.parse_args()


async def async_main() -> int:
    args = parse_args()
    workspace = Path(__file__).resolve().parents[1]
    config_path = (workspace / args.config).resolve()
    config = load_mcp_config(config_path)
    config_issues = validate_config_inputs(
        config,
        args.server,
        args.env_strict,
    )

    if args.config_only:
        error_issues = has_error_issues(config_issues)
        if args.json:
            payload: dict[str, Any] = {
                "summary": {
                    "total": 0,
                    "ok": 0,
                    "fail": 0,
                    "all_ok": not error_issues,
                },
                "servers": [],
                "config_issues": [asdict(issue) for issue in config_issues],
                "mode": "config-only",
            }
            print(json.dumps(payload, indent=2))
        else:
            if config_issues:
                for issue in config_issues:
                    level = issue.severity.upper()
                    print(f"CONFIG {level} - {issue.code}: {issue.detail}")
            else:
                print("Config OK - no static MCP config issues found.")
        return 1 if error_issues else 0

    results = await validate_servers(workspace, config_path, args.server)

    if not results:
        if args.json:
            print(
                json.dumps(
                    {
                        "summary": {
                            "total": 0,
                            "ok": 0,
                            "fail": 0,
                            "all_ok": False,
                        },
                        "servers": [],
                        "config_issues": [asdict(issue) for issue in config_issues],
                        "error": ("No MCP servers matched the requested selection."),
                    },
                    indent=2,
                )
            )
        else:
            print("No MCP servers matched the requested selection.")
        return 1

    if args.json:
        payload = results_to_json(results)
        payload["config_issues"] = [asdict(issue) for issue in config_issues]
        print(json.dumps(payload, indent=2))
        has_failures = any(not result.ok for result in results)
        return 1 if has_failures or has_error_issues(config_issues) else 0

    if config_issues:
        for issue in config_issues:
            level = issue.severity.upper()
            print(f"CONFIG {level} - {issue.code}: {issue.detail}")

    failures = 0
    for result in results:
        status = "OK" if result.ok else "FAIL"
        print(f"{result.name}: {status} - {result.detail}")
        if not result.ok:
            failures += 1

    return 1 if failures or has_error_issues(config_issues) else 0


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
