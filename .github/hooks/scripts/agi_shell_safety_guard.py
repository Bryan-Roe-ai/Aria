#!/usr/bin/env python3
"""PreToolUse shell safety guard for AGI agent inline hooks.

Purpose:
  Block clearly dangerous terminal command patterns before execution.

Events handled:
  - PreToolUse

Behavior:
  - For terminal execution tools, inspects command text.
    - Hard-blocks catastrophic and high-risk patterns.

Exit codes:
  - 1: blocked
  - 0: allow (including warning-only cases and parse failures)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sys
import time
from typing import Any, Iterable

EXEC_TOOLS = {
    "run_in_terminal",
    "execution_subagent",
    "create_and_run_task",
    "run_task",
    "send_to_terminal",
}

BLOCK_PATTERNS = [
    re.compile(r"(^|\s)rm\s+-rf\s+/(\s|$)"),
    re.compile(r"(^|\s)sudo\s+rm\s+-rf\s+/(\s|$)"),
    re.compile(r"(^|\s)mkfs(\.|\s)", re.IGNORECASE),
    re.compile(r"(^|\s)fdisk(\s|$)", re.IGNORECASE),
    re.compile(r"(^|\s)dd\s+.*\bof=/dev/(sd|nvme|vd|xvd)", re.IGNORECASE),
    re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:", re.IGNORECASE),
    re.compile(r"(^|\s)kill\s+-9\s+-1(\s|$)", re.IGNORECASE),
]

HIGH_RISK_BLOCK_PATTERNS = [
    re.compile(r"(^|\s)curl\s+[^|\n]+\|\s*(bash|sh)(\s|$)", re.IGNORECASE),
    re.compile(r"(^|\s)wget\s+[^|\n]+\|\s*(bash|sh)(\s|$)", re.IGNORECASE),
    re.compile(r"(^|\s)sudo\s+", re.IGNORECASE),
    re.compile(r"(^|\s)chmod\s+-R\s+777\s+/(\s|$)", re.IGNORECASE),
]

OVERRIDE_SHA256_ENV = "AGI_SHELL_OVERRIDE_SHA256"
OVERRIDE_ACK_ENV = "AGI_SHELL_OVERRIDE_ACK"
OVERRIDE_ACK_VALUE = "I_UNDERSTAND_THE_RISK"
OVERRIDE_EXPIRES_EPOCH_ENV = "AGI_SHELL_OVERRIDE_EXPIRES_EPOCH"
OVERRIDE_MAX_WINDOW_SECONDS_ENV = "AGI_SHELL_OVERRIDE_MAX_WINDOW_SECONDS"
OVERRIDE_DEFAULT_MAX_WINDOW_SECONDS = 300
OVERRIDE_NONCE_ENV = "AGI_SHELL_OVERRIDE_NONCE"
OVERRIDE_NONCE_MIN_LEN = 12
OVERRIDE_REQUEST_ID_ENV = "AGI_SHELL_OVERRIDE_REQUEST_ID"
OVERRIDE_REQUEST_ID_MIN_LEN = 8
OVERRIDE_REQUEST_ID_PATTERN_ENV = "AGI_SHELL_OVERRIDE_REQUEST_ID_PATTERN"


def _walk(obj: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v
            yield from _walk(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


def _tool_name(payload: dict[str, Any]) -> str:
    params_obj = payload.get("parameters")
    params: dict[str, Any] = params_obj if isinstance(params_obj, dict) else {}
    name = (
        payload.get("toolName")
        or payload.get("tool_name")
        or payload.get("name")
        or params.get("toolName")
        or params.get("tool_name")
        or params.get("name")
    )
    return name if isinstance(name, str) else ""


def _command_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []
    interesting_keys = {"command", "cmd", "args",
                        "goal", "explanation", "input", "text"}
    for key, val in _walk(payload):
        key_l = key.lower()
        if key_l not in interesting_keys:
            continue
        if isinstance(val, str):
            parts.append(val)
        elif isinstance(val, list):
            parts.extend(str(x) for x in val)
    return "\n".join(parts)


def _match_any(patterns: list[re.Pattern[str]], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def _cmd_sha256(command_text: str) -> str:
    return hashlib.sha256(command_text.strip().encode("utf-8")).hexdigest()


def _validate_request_id_format(request_id: str) -> str:
    """Validate request_id against optional pattern and return status message.

    Returns:
        Formatted status message for audit logging.
        - If no pattern is set: format check disabled
        - If matches: format matches pattern
        - If doesn't match: format mismatch (expected X, got Y)
        - If pattern error: pattern error, allowing override
    """
    pattern_str = os.environ.get(OVERRIDE_REQUEST_ID_PATTERN_ENV, "").strip()
    if not pattern_str:
        return "(request-id format check not configured)"

    try:
        pattern = re.compile(pattern_str)
    except re.error as e:
        return f"(pattern error: {e}, allowing override)"

    if pattern.match(request_id):
        return "(request-id format matches pattern)"
    return (
        f"(request-id format mismatch: expected {pattern_str}, "
        f"got {request_id})"
    )


def _is_high_risk_override_allowed(command_text: str) -> bool:
    expected_sha = os.environ.get(OVERRIDE_SHA256_ENV, "").strip().lower()
    ack = os.environ.get(OVERRIDE_ACK_ENV, "").strip()
    expires_raw = os.environ.get(OVERRIDE_EXPIRES_EPOCH_ENV, "").strip()
    max_window_raw = os.environ.get(
        OVERRIDE_MAX_WINDOW_SECONDS_ENV, "").strip()
    nonce = os.environ.get(OVERRIDE_NONCE_ENV, "").strip()
    request_id = os.environ.get(OVERRIDE_REQUEST_ID_ENV, "").strip()

    if (
        not expected_sha
        or ack != OVERRIDE_ACK_VALUE
        or not expires_raw
        or len(nonce) < OVERRIDE_NONCE_MIN_LEN
        or len(request_id) < OVERRIDE_REQUEST_ID_MIN_LEN
    ):
        return False

    try:
        expires_epoch = int(expires_raw)
    except ValueError:
        return False

    try:
        max_window_seconds = (
            int(max_window_raw)
            if max_window_raw
            else OVERRIDE_DEFAULT_MAX_WINDOW_SECONDS
        )
    except ValueError:
        max_window_seconds = OVERRIDE_DEFAULT_MAX_WINDOW_SECONDS

    max_window_seconds = max(1, max_window_seconds)
    now = int(time.time())
    if expires_epoch < now:
        return False
    if (expires_epoch - now) > max_window_seconds:
        return False

    return hmac.compare_digest(_cmd_sha256(command_text), expected_sha)


def main() -> None:
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit(0)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit(0)

    event = os.environ.get("COPILOT_HOOK_EVENT", "PreToolUse")
    if event != "PreToolUse":
        sys.exit(0)

    tool = _tool_name(payload).lower()
    if tool not in EXEC_TOOLS:
        sys.exit(0)

    cmd = _command_text(payload)
    if not cmd.strip():
        sys.exit(0)

    catastrophic_match = _match_any(BLOCK_PATTERNS, cmd)
    high_risk_match = _match_any(HIGH_RISK_BLOCK_PATTERNS, cmd)

    if catastrophic_match:
        print(
            (
                "🛑 BLOCKED by AGI shell safety guard: command matches "
                "catastrophic pattern (no override allowed)."
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    if high_risk_match:
        if _is_high_risk_override_allowed(cmd):
            request_id = os.environ.get(OVERRIDE_REQUEST_ID_ENV, "").strip()
            format_msg = _validate_request_id_format(request_id)
            print(
                (
                    "⚠️ AGI shell safety override accepted for exact "
                    "high-risk command hash "
                    f"(request_id={request_id}) {format_msg}."
                ),
                file=sys.stdout,
            )
            sys.exit(0)
        print(
            (
                "🛑 BLOCKED by AGI shell safety guard: command matches "
                "high-risk pattern. To allow only this exact command once, "
                "set AGI_SHELL_OVERRIDE_ACK, "
                "AGI_SHELL_OVERRIDE_SHA256, "
                "AGI_SHELL_OVERRIDE_EXPIRES_EPOCH, "
                "AGI_SHELL_OVERRIDE_NONCE, and "
                "AGI_SHELL_OVERRIDE_REQUEST_ID."
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
