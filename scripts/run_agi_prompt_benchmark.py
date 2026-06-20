#!/usr/bin/env python3
"""Run a reproducible AGI prompt benchmark against Chat CLI providers.

Outputs JSON artifacts under data_out/ai_eval/ for easy weekly comparison.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_PROMPTS = [
    "Explain the goal of this AGI project in one sentence.",
    "Break the project into 3 phases with clear outcomes.",
    "List top 5 technical risks and rank by impact.",
    "Propose a minimal plan→act→reflect loop in pseudocode.",
    "Summarize how memory should be used safely in this system.",
    "Give 3 examples of good tool-use requests.",
    "Give 3 examples of unsafe tool-use requests and why.",
    "Write a concise system prompt for an AGI assistant.",
    "Compare short-term memory vs long-term memory for this use case.",
    "Suggest metrics for task success, latency, and safety.",
    "Convert a vague user request into actionable subtasks.",
    "Detect contradictions in a 5-step plan and propose fixes.",
    "Provide a fallback strategy when provider API is unavailable.",
    "Explain tradeoffs between larger vs smaller local models.",
    "Create a daily checklist for maintaining model quality.",
    "Define what constitutes a critical safety incident.",
    "Draft a release gate policy for v1 deployment.",
    "Propose an evaluation rubric for reasoning quality.",
    "Generate a structured JSON response schema for tool calls.",
    "Explain how to handle ambiguous user commands safely.",
    "Write 5 adversarial prompts to test guardrails.",
    "Suggest mitigation steps when hallucination is detected.",
    "Recommend observability logs for debugging failures.",
    "Turn benchmark failures into prioritized backlog items.",
    "Propose a rollback plan after a bad model release.",
    "Explain how to test determinism in tool execution.",
    "Create a prompt to evaluate planning depth.",
    "Suggest a method to estimate latency p95 from sample runs.",
    "Produce a one-paragraph weekly status summary template.",
    "Give a go/no-go recommendation format for release review.",
]


@dataclass
class PromptResult:
    index: int
    prompt: str
    ok: bool
    elapsed_ms: float
    exit_code: int
    provider_line: str | None
    assistant_line: str | None
    error: str | None


def _extract_first_line(prefix: str, text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().startswith(prefix):
            return line.strip()
    return None


def _run_prompt(provider: str, prompt: str, timeout_s: int) -> PromptResult:
    cmd = [
        ".venv/bin/python",
        "ai-projects/chat-cli/src/chat_cli.py",
        "--provider",
        provider,
        "--once",
        prompt,
    ]
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        provider_line = _extract_first_line("Provider:", stdout)
        assistant_line = _extract_first_line("assistant>", stdout)
        ok = completed.returncode == 0 and assistant_line is not None
        error = None if ok else (stderr.strip() or "missing assistant output")
        return PromptResult(
            index=0,
            prompt=prompt,
            ok=ok,
            elapsed_ms=round(elapsed_ms, 2),
            exit_code=completed.returncode,
            provider_line=provider_line,
            assistant_line=assistant_line,
            error=error,
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return PromptResult(
            index=0,
            prompt=prompt,
            ok=False,
            elapsed_ms=round(elapsed_ms, 2),
            exit_code=124,
            provider_line=None,
            assistant_line=None,
            error=f"timeout after {timeout_s}s",
        )


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    idx = int(0.95 * (len(ordered) - 1))
    return ordered[idx]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run AGI prompt benchmark via chat_cli.py"
    )
    parser.add_argument(
        "--provider",
        default="lmstudio",
        help="chat provider to benchmark",
    )
    parser.add_argument(
        "--max-prompts",
        type=int,
        default=0,
        help="optional cap for quicker runs (0 = all prompts)",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=120,
        help="per-prompt timeout in seconds",
    )
    parser.add_argument(
        "--out-dir",
        default="data_out/ai_eval",
        help="output directory for benchmark artifacts",
    )
    args = parser.parse_args()

    if args.max_prompts and args.max_prompts > 0:
        prompts = DEFAULT_PROMPTS[: args.max_prompts]
    else:
        prompts = DEFAULT_PROMPTS
    run_started = datetime.now(UTC)

    results: list[PromptResult] = []
    for idx, prompt in enumerate(prompts, start=1):
        result = _run_prompt(args.provider, prompt, args.timeout_seconds)
        result.index = idx
        results.append(result)
        status = "ok" if result.ok else "fail"
        print(f"[{idx:02d}/{len(prompts)}] {status} {result.elapsed_ms:.0f}ms")

    ok_count = sum(1 for r in results if r.ok)
    latencies = [r.elapsed_ms for r in results if r.ok]
    summary = {
        "provider": args.provider,
        "started_at": run_started.isoformat(),
        "completed_at": datetime.now(UTC).isoformat(),
        "prompt_count": len(results),
        "ok_count": ok_count,
        "fail_count": len(results) - ok_count,
        "success_rate": (
            round((ok_count / len(results) * 100.0), 2) if results else 0.0
        ),
        "latency_ms_avg": (
            round(statistics.fmean(latencies), 2) if latencies else 0.0
        ),
        "latency_ms_median": (
            round(statistics.median(latencies), 2) if latencies else 0.0
        ),
        "latency_ms_p95": round(_p95(latencies), 2) if latencies else 0.0,
    }

    payload = {
        "summary": summary,
        "results": [asdict(r) for r in results],
    }

    out_dir = Path(args.out_dir)
    timestamp = run_started.strftime("%Y%m%dT%H%M%SZ")
    latest_path = out_dir / "agi_prompt_benchmark_latest.json"
    stamped_path = out_dir / f"agi_prompt_benchmark_{timestamp}.json"
    _write_json(latest_path, payload)
    _write_json(stamped_path, payload)

    print("\n=== Benchmark summary ===")
    print(json.dumps(summary, indent=2))
    print(f"\nWrote: {latest_path}")
    print(f"Wrote: {stamped_path}")

    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
