#!/usr/bin/env python3
"""Run pytest across test-file shards without external dependencies.

This script provides a fallback parallel path for local development when
pytest-xdist is unavailable. It shards discovered test files across multiple
pytest subprocesses and returns a non-zero exit code if any shard fails.
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import cast

TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")


def parse_args(argv: Sequence[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run pytest in parallel by sharding test files."
    )
    parser.add_argument(
        "paths", nargs="*", help="Test files or directories to run."
    )
    parser.add_argument(
        "--workers",
        default="auto",
        help="Number of parallel workers to use, or 'auto' (default).",
    )
    parser.add_argument(
        "--min-files-per-worker",
        type=int,
        default=2,
        help="Avoid spawning extra workers when there are too few test files.",
    )
    args, pytest_args = parser.parse_known_args(argv)
    return args, pytest_args


def normalize_workers(
    value: str, file_count: int, min_files_per_worker: int
) -> int:
    if file_count <= 1:
        return 1
    if value == "auto":
        requested = os.cpu_count() or 1
    else:
        requested = max(1, int(value))
    capped = min(requested, file_count)
    if min_files_per_worker > 1:
        capped = min(
            capped,
            max(1, math.ceil(file_count / min_files_per_worker)),
        )
    return max(1, capped)


def discover_test_files(paths: Iterable[str]) -> list[str]:
    discovered: list[str] = []
    seen: list[str] = []
    for raw_path in paths or ["tests"]:
        path = Path(raw_path)
        if path.is_file():
            normalized = str(path)
            if normalized not in seen:
                seen.append(normalized)
                discovered.append(normalized)
            continue
        if not path.exists():
            continue
        for pattern in TEST_FILE_PATTERNS:
            for file_path in sorted(path.rglob(pattern)):
                normalized = str(file_path)
                if normalized not in seen:
                    seen.append(normalized)
                    discovered.append(normalized)
    return discovered


def shard_files(files: Sequence[str], worker_count: int) -> list[list[str]]:
    shards: list[list[str]] = [[] for _ in range(worker_count)]
    shard_sizes = [0] * worker_count
    weighted_files: list[tuple[str, int]] = []
    for file_path in files:
        path = Path(file_path)
        weight = path.stat().st_size if path.exists() else 0
        weighted_files.append((file_path, weight))

    weighted_files.sort(key=lambda item: item[1], reverse=True)

    for file_path, weight in weighted_files:
        shard_index = min(
            range(worker_count), key=lambda index: shard_sizes[index]
        )
        shards[shard_index].append(file_path)
        shard_sizes[shard_index] += weight
    return [shard for shard in shards if shard]


def run_serial(paths: Sequence[str], pytest_args: Sequence[str]) -> int:
    command = [sys.executable, "-m", "pytest", *paths, *pytest_args]
    return subprocess.run(command, check=False).returncode


def run_parallel(
    files: Sequence[str], pytest_args: Sequence[str], worker_count: int
) -> int:
    shards = shard_files(files, worker_count)
    print(
        "🧪 builtin parallel pytest fallback enabled "
        f"({len(shards)} workers across {len(files)} files)"
    )
    processes: list[tuple[int, list[str], subprocess.Popen[str]]] = []
    for index, shard in enumerate(shards, start=1):
        command = [sys.executable, "-m", "pytest", *shard, *pytest_args]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        processes.append((index, shard, process))

    exit_code = 0
    for index, shard, process in processes:
        output, _ = process.communicate()
        print(
            f"\n===== pytest shard {index}/{len(shards)} "
            f"({len(shard)} files) ====="
        )
        if output:
            print(output, end="" if output.endswith("\n") else "\n")
        result_code = process.returncode
        if result_code is not None and result_code != 0:
            exit_code = result_code
    return cast(int, exit_code)


def main(argv: Sequence[str]) -> int:
    args, pytest_args = parse_args(argv)
    files = discover_test_files(args.paths)
    if not files:
        print(
            "No test files discovered; falling back to pytest with "
            "the original paths.",
            file=sys.stderr,
        )
        return run_serial(args.paths or ["tests"], pytest_args)

    worker_count = normalize_workers(
        args.workers, len(files), args.min_files_per_worker
    )
    if worker_count <= 1:
        print(
            "🧪 builtin parallel pytest fallback using serial mode "
            "(not enough files to shard)"
        )
        return run_serial(args.paths or ["tests"], pytest_args)
    return run_parallel(files, pytest_args, worker_count)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
