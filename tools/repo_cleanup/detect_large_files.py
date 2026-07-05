from pathlib import Path

THRESHOLD = 2000

for path in Path(".").rglob("*.py"):
    try:
        lines = path.read_text(encoding="utf-8").count("\n")
        if lines > THRESHOLD:
            print(f"LARGE FILE: {path} ({lines} lines)")
    except Exception:
        pass
