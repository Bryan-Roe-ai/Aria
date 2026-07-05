from pathlib import Path

ROOT = Path(".")

FORBIDDEN_DIRS = [
    "__pycache__",
    ".venv",
    ".venv-linux",
    "logs",
]

FORBIDDEN_PATTERNS = [
    "*.pyc",
    "coverage*",
    "tmp*",
]


def scan_forbidden_dirs():
    found = []
    for forbidden in FORBIDDEN_DIRS:
        found.extend(ROOT.rglob(forbidden))
    return found


def scan_patterns():
    found = []
    for pattern in FORBIDDEN_PATTERNS:
        found.extend(ROOT.rglob(pattern))
    return found


def root_clutter_score():
    entries = list(ROOT.iterdir())
    return len(entries)


if __name__ == "__main__":
    print("Repository structure validation")
    print("-" * 40)

    bad_dirs = scan_forbidden_dirs()
    bad_patterns = scan_patterns()

    if bad_dirs:
        print("\nForbidden directories detected:")
        for item in bad_dirs:
            print(f" - {item}")

    if bad_patterns:
        print("\nForbidden file patterns detected:")
        for item in bad_patterns:
            print(f" - {item}")

    clutter = root_clutter_score()
    print(f"\nRoot entry count: {clutter}")

    if clutter > 30:
        print("WARNING: Root directory is heavily cluttered.")

    if not bad_dirs and not bad_patterns:
        print("\nRepository structure looks clean.")
