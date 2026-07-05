from pathlib import Path

root = Path(".")

py_files = list(root.rglob("*.py"))
md_files = list(root.rglob("*.md"))

score = 100

if len(list(root.iterdir())) > 40:
    score -= 20

large_files = 0
for path in py_files:
    try:
        lines = path.read_text(encoding="utf-8").count("\n")
        if lines > 2000:
            large_files += 1
    except Exception:
        pass

score -= large_files * 5
score = max(score, 0)

print("Repository Scorecard")
print("-" * 40)
print(f"Python files: {len(py_files)}")
print(f"Markdown files: {len(md_files)}")
print(f"Oversized modules: {large_files}")
print(f"Maintainability score: {score}/100")
