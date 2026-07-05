from pathlib import Path

EXPECTED = {
    "apps": ["web", "aria"],
    "services": ["function", "automation"],
    "tools": ["repo_cleanup"],
}

print("Architecture drift analysis")
print("-" * 40)

for folder, keywords in EXPECTED.items():
    found = False
    for path in Path(".").iterdir():
        if path.is_dir():
            for keyword in keywords:
                if keyword in path.name.lower():
                    found = True

    if not found:
        print(f"Missing expected architecture domain: {folder}")
