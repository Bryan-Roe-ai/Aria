from pathlib import Path

ROOT = Path(".")
OUT = ROOT / "docs" / "reports"
OUT.mkdir(parents=True, exist_ok=True)

report = OUT / "repo-inventory.md"

with report.open("w", encoding="utf-8") as f:
    f.write("# Repository Inventory\n\n")

    for item in sorted(ROOT.iterdir()):
        if item.name.startswith(".git"):
            continue

        kind = "Directory" if item.is_dir() else "File"
        f.write(f"- {kind}: `{item.name}`\n")

print(f"Generated {report}")
