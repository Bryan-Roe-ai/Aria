from collections import defaultdict
from pathlib import Path

hashes = defaultdict(list)

for path in Path(".").rglob("*.py"):
    try:
        text = path.read_text(encoding="utf-8")
        hashes[hash(text)].append(str(path))
    except Exception:
        pass

for _, files in hashes.items():
    if len(files) > 1:
        print("Potential duplicate files:")
        for f in files:
            print("-", f)
