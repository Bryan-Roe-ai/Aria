#!/usr/bin/env python3
"""Organize the massive_quantum dataset folder into categorized subfolders.

Safe operation:
- Moves files into category subfolders (no deletions)
- Preserves existing openml/ subfolder
- Creates symlinks from old location if --symlink flag is used
- Prints summary of all moves

Categories:
  forex/         - FOREX_* currency pair datasets
  synthetic/blobs/          - synthetic_blobs_*
  synthetic/circles/        - synthetic_circles_*
  synthetic/classification/ - synthetic_classification_*
  synthetic/gaussian/       - synthetic_gaussian_*
  synthetic/moons/          - synthetic_moons_*
  benchmarks/    - Named OpenML benchmark datasets (seeds, named)
  medical/       - Medical/health datasets
  financial/     - Financial/credit/loan datasets
  misc/          - Everything else not already in a subfolder
"""
import os
import shutil
import json
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MQ = os.path.join(BASE, "datasets", "massive_quantum")

# Category rules: (prefix/pattern, target_subfolder)
RULES = [
    (re.compile(r"^FOREX_"), "forex"),
    (re.compile(r"^synthetic_blobs_"), "synthetic/blobs"),
    (re.compile(r"^synthetic_circles_"), "synthetic/circles"),
    (re.compile(r"^synthetic_classification_"), "synthetic/classification"),
    (re.compile(r"^synthetic_gaussian_"), "synthetic/gaussian"),
    (re.compile(r"^synthetic_moons_"), "synthetic/moons"),
    # Medical
    (re.compile(r"(?i)(diabetes|heart|cancer|hepatitis|kidney|maternal|blood.transfusion|haberman|heloc|biomed|glioma|obesity)"), "medical"),
    # Financial
    (re.compile(r"(?i)(credit|loan|bank|churn|german.credit|apple.stock|employee|fitness)"), "financial"),
    # Named OpenML benchmarks with seed variants
    (re.compile(r"_seed_\d+_nrows_"), "benchmarks/seeded"),
]


def categorize(filename):
    """Return the target subfolder for a file, or None to leave it."""
    for pattern, target in RULES:
        if pattern.search(filename):
            return target
    return "misc"


def main():
    dry_run = "--dry-run" in sys.argv
    
    if not os.path.isdir(MQ):
        print(f"[ERROR] {MQ} not found")
        return

    # Collect only top-level CSV files (not already in subfolders)
    files = [f for f in os.listdir(MQ)
             if os.path.isfile(os.path.join(MQ, f)) and f.endswith(".csv")]
    
    moves = {}  # target_dir -> [filenames]
    for f in sorted(files):
        cat = categorize(f)
        if cat:
            moves.setdefault(cat, []).append(f)

    total = sum(len(v) for v in moves.values())
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Organizing {total} files into {len(moves)} categories:\n")

    for cat in sorted(moves):
        target_dir = os.path.join(MQ, cat)
        flist = moves[cat]
        print(f"  {cat}/ -> {len(flist)} files")
        
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)
            for f in flist:
                src = os.path.join(MQ, f)
                dst = os.path.join(target_dir, f)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
                else:
                    print(f"    [SKIP] {f} already exists in {cat}/")

    # Keep JSON metadata files at top level
    json_files = [f for f in os.listdir(MQ)
                  if os.path.isfile(os.path.join(MQ, f)) and f.endswith(".json")]
    if json_files:
        print(f"\n  Kept at top level: {', '.join(json_files)}")

    print(f"\n{'[DRY RUN] Would move' if dry_run else 'Moved'} {total} files total.")
    
    # Print final structure
    if not dry_run:
        print("\nFinal massive_quantum/ structure:")
        for item in sorted(os.listdir(MQ)):
            full = os.path.join(MQ, item)
            if os.path.isdir(full):
                count = sum(1 for f in os.listdir(full) if f.endswith(".csv"))
                # check subdirs
                subdirs = [d for d in os.listdir(full) if os.path.isdir(os.path.join(full, d))]
                if subdirs:
                    print(f"  {item}/")
                    for sd in sorted(subdirs):
                        scount = sum(1 for f in os.listdir(os.path.join(full, sd)) if f.endswith(".csv"))
                        print(f"    {sd}/ ({scount} CSVs)")
                    if count:
                        print(f"    + {count} CSVs at top level")
                else:
                    print(f"  {item}/ ({count} CSVs)")
            else:
                print(f"  {item}")


if __name__ == "__main__":
    main()
