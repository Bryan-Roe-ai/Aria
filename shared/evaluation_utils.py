#!/usr/bin/env python
"""
Shared evaluation utilities for model evaluation scripts.

This module contains common functions used across multiple evaluation scripts
to avoid code duplication.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List


def load_jsonl(path: Path, max_samples: int | None = None) -> List[Dict[str, Any]]:
    """
    Load data from a JSONL file (one JSON object per line).
    
    Args:
        path: Path to the JSONL file
        max_samples: Maximum number of samples to load (None = load all)
        
    Returns:
        List of dictionaries loaded from the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(path)
    data: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if max_samples is not None and i >= max_samples:
                break
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data


def load_dataset(path: Path, max_samples: int | None = None) -> List[Dict[str, Any]]:
    """
    Load data from various formats (JSONL, JSON array, or CSV).
    
    Supports:
    - JSONL (one object per line)
    - JSON array
    - CSV (first column is input, second column is label/expected)
    
    Args:
        path: Path to the dataset file
        max_samples: Maximum number of samples to load (None = load all)
        
    Returns:
        List of dictionaries loaded from the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(path)

    data: List[Dict[str, Any]] = []
    # Try JSONL (one object per line)
    try:
        with path.open("r", encoding="utf-8") as f:
            # If file looks like a JSON array, parsing as JSON will succeed
            text = f.read().strip()
            if not text:
                return []
            if text.startswith("["):
                objs = json.loads(text)
                if isinstance(objs, list):
                    data = objs
                else:
                    data = [objs]
            else:
                # treat as JSONL
                f.seek(0)
                for i, line in enumerate(f):
                    if max_samples is not None and i >= max_samples:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    data.append(json.loads(line))
    except json.JSONDecodeError:
        # Fallback to CSV (simple) - first column input, second expected
        data = []
        with path.open("r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if max_samples is not None and i >= max_samples:
                    break
                if not row:
                    continue
                inp = row[0]
                expected = row[1] if len(row) > 1 else None
                data.append({"input": inp, "expected": expected})

    if max_samples is not None:
        return data[:max_samples]
    return data


def naive_predict(example: Dict[str, Any]) -> str:
    """
    Simple local fallback predictor for testing.
    
    Returns a deterministic echo response based on the example input.
    Handles various common input formats (input field, messages array, etc).
    
    Args:
        example: Dictionary containing the input data
        
    Returns:
        Echo response string
    """
    # Extract text from common patterns
    if "input" in example and isinstance(example["input"], str):
        content = example["input"].strip()
        return f"echo: {content}"

    # Chat-style messages
    msgs = example.get("messages") or example.get("conversation") or []
    if isinstance(msgs, list) and msgs:
        # find last user message
        last_user = None
        for m in reversed(msgs):
            if isinstance(m, dict) and m.get("role") == "user":
                last_user = m.get("content", "")
                break
        if last_user is None:
            last_user = msgs[-1].get("content", "") if isinstance(msgs[-1], dict) else str(msgs[-1])
        return f"echo: {last_user.strip()}"

    # Fallback
    return "echo:"
