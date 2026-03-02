"""Pytest configuration for QAI test suite.

This conftest ensures that the scripts package is importable during tests.
"""
import sys
import importlib.util
from pathlib import Path

# Add project root to Python path for importing scripts
REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Add tools/talk-to-ai/src for chat_providers imports
TALK_TO_AI_SRC = REPO_ROOT / "tools" / "talk-to-ai" / "src"
if str(TALK_TO_AI_SRC) not in sys.path:
    sys.path.insert(0, str(TALK_TO_AI_SRC))

# === ensure test dependencies ===
# When the virtual environment isn't activated properly, imports can fail
# during collection. To make the repo "just work" for QAI developers we
# attempt to install a handful of common test libraries on-the-fly.
import subprocess

# Mapping of import names to PyPI package names (for cases where they differ)
REQUIRED_MODULES = [
    ("yaml", "PyYAML"),        # PyYAML for YAML parsing tests
    ("flask", "flask"),         # web app security/integration tests
    ("requests", "requests"),   # HTTP clients used by integration tests
    ("PIL", "Pillow"),          # Pillow for image tests
    ("torch", "torch"),         # PyTorch for model-based tests
    ("pennylane", "pennylane"), # PennyLane quantum ML framework
]

for import_name, package_name in REQUIRED_MODULES:
    try:
        if importlib.util.find_spec(import_name) is None:
            print(f"[conftest] installing missing module {import_name}")
            subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)
    except Exception as exc:  # pragma: no cover
        print(f"[conftest] failed to install {import_name}: {exc}")
