#!/usr/bin/env python3
"""
Dataset Discovery & Validation Tool

Lists all available datasets and validates they can be loaded.
Useful for:
  - Understanding available training data
  - Checking dataset health/integrity
  - Finding datasets by category, size, or features
"""
import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Tuple

BASE_PATH = Path(__file__).parent.parent / "datasets"

def discover_all_datasets() -> Dict[str, Dict]:
    """Discover all CSV datasets recursively."""
    datasets = {}

    # Walk all directories looking for CSVs
    for csv_path in BASE_PATH.rglob("*.csv"):
        name = csv_path.stem
        rel_path = csv_path.relative_to(BASE_PATH)
        size = csv_path.stat().st_size

        # Determine category from path
        parts = rel_path.parts
        if parts[0] == 'quantum':
            category = 'quantum'
        elif parts[0] == 'massive_quantum':
            if len(parts) > 1:
                category = f"massive_quantum/{parts[1]}"
            else:
                category = "massive_quantum/root"
        else:
            category = parts[0]

        datasets[name] = {
            'path': str(rel_path),
            'full_path': str(csv_path),
            'category': category,
            'size_bytes': size,
            'size_mb': round(size / 1e6, 2)
        }

    return datasets

def load_index() -> Dict:
    """Load dataset index if available."""
    idx_path = BASE_PATH / "dataset_index.json"
    if idx_path.exists():
        with open(idx_path) as f:
            return json.load(f)
    return {}

def validate_dataset(csv_path: Path) -> Tuple[bool, str]:
    """Validate a CSV dataset is readable."""
    try:
        import pandas as pd
        df = pd.read_csv(csv_path, nrows=1)
        rows = sum(1 for _ in open(csv_path)) - 1
        cols = len(df.columns)
        return True, f"{rows} rows × {cols} cols"
    except Exception as e:
        return False, str(e)[:50]

def list_datasets(category: str = None, limit: int = None) -> None:
    """List all discovered datasets, optionally filtered by category."""
    datasets = discover_all_datasets()
    index = load_index()

    # Filter by category if provided
    if category:
        datasets = {k: v for k, v in datasets.items() if category in v['category']}

    # Sort by category then name
    sorted_ds = sorted(datasets.items(), key=lambda x: (x[1]['category'], x[0]))

    print(f"\nDiscovered {len(sorted_ds)} datasets:")
    print("-" * 80)
    print(f"{'Name':<30} {'Category':<20} {'Size':<12} {'Path':<40}")
    print("-" * 80)

    current_cat = None
    count = 0
    for name, info in sorted_ds:
        if limit and count >= limit:
            print(f"... and {len(sorted_ds) - count} more")
            break

        if info['category'] != current_cat:
            current_cat = info['category']

        path = info['path'][-38:] if len(info['path']) > 38 else info['path']
        print(f"{name:<30} {info['category']:<20} {info['size_mb']:>10} MB  {path:>38}")
        count += 1

    print("-" * 80)

def validate_all_datasets() -> None:
    """Validate all datasets are readable."""
    datasets = discover_all_datasets()
    print(f"\nValidating {len(datasets)} datasets...")

    valid = 0
    invalid = 0

    for name, info in sorted(datasets.items()):
        full = Path(info['full_path'])
        is_valid, msg = validate_dataset(full)
        if is_valid:
            print(f"  ✓ {name:<30} {msg}")
            valid += 1
        else:
            print(f"  ✗ {name:<30} ERROR: {msg}")
            invalid += 1

    print(f"\nResults: {valid} valid, {invalid} invalid")

def get_datasets_by_category(category: str) -> List[str]:
    """Get all dataset names in a category."""
    datasets = discover_all_datasets()
    return sorted([k for k, v in datasets.items() if v['category'] == category])

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'validate':
            validate_all_datasets()
        elif cmd == 'list':
            cat = sys.argv[2] if len(sys.argv) > 2 else None
            list_datasets(category=cat)
        elif cmd == 'quantum':
            print("\nQuantum datasets:")
            for ds in get_datasets_by_category('quantum'):
                print(f"  - {ds}")
        elif cmd == 'chat':
            print("\nChat datasets:")
            for ds in get_datasets_by_category('chat'):
                print(f"  - {ds}")
        else:
            print(f"Unknown command: {cmd}")
    else:
        # Default: list all with validation
        list_datasets()
        print("\nRun with 'validate' to check all datasets are readable")
        print("Run with 'quantum' or 'chat' to list specific categories")
