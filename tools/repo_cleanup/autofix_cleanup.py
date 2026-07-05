import shutil
from pathlib import Path

ROOT = Path(".")

REMOVE_DIRS = [
    "__pycache__",
    ".pytest_cache",
]

REMOVE_PATTERNS = [
    "*.pyc",
    "coverage*",
]

MOVE_TO_DATA_OUT = [
    "logs",
]


def remove_dirs():
    for dirname in REMOVE_DIRS:
        for path in ROOT.rglob(dirname):
            if path.is_dir():
                print(f"Removing directory: {path}")
                shutil.rmtree(path, ignore_errors=True)


def remove_patterns():
    for pattern in REMOVE_PATTERNS:
        for path in ROOT.rglob(pattern):
            if path.is_file():
                print(f"Removing file: {path}")
                path.unlink(missing_ok=True)


def move_generated_dirs():
    data_out = ROOT / "data_out"
    data_out.mkdir(exist_ok=True)

    for name in MOVE_TO_DATA_OUT:
        for path in ROOT.glob(name):
            if path.exists() and path.name != "data_out":
                target = data_out / path.name
                print(f"Moving {path} -> {target}")
                if target.exists():
                    shutil.rmtree(target, ignore_errors=True)
                shutil.move(str(path), str(target))


if __name__ == "__main__":
    remove_dirs()
    remove_patterns()
    move_generated_dirs()
    print("Cleanup automation complete.")
