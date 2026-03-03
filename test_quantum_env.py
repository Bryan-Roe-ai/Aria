#!/usr/bin/env python
"""Quick test to verify quantum training can import and run"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

# Test imports
try:
    import numpy as np
    print(f"✓ numpy {np.__version__}")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print(f"✓ pandas {pd.__version__}")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")
    sys.exit(1)

try:
    import torch
    print(f"✓ torch {torch.__version__}")
except ImportError as e:
    print(f"✗ torch import failed: {e}")
    sys.exit(1)

try:
    from sklearn import datasets  # noqa: F401
    print("✓ sklearn available")
except ImportError as e:
    print(f"✗ sklearn import failed: {e}")
    sys.exit(1)

try:
    import qiskit
    print(f"✓ qiskit {qiskit.__version__}")
except ImportError as e:
    print(f"✗ qiskit import failed: {e}")
    sys.exit(1)

try:
    import pennylane as qml
    print(f"✓ pennylane {qml.__version__}")
except ImportError as e:
    print(f"✗ pennylane import failed: {e}")
    sys.exit(1)

print("\n✅ All core dependencies installed!")
print("\nNow testing quantum training module import...")

try:
    # Import the training module
    sys.path.insert(0, str(REPO_ROOT / "quantum"))
    import train_custom_dataset  # noqa: F401
    print("✓ train_custom_dataset module imported successfully")
except Exception as e:
    print(f"✗ Failed to import train_custom_dataset: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ ENVIRONMENT READY FOR QUANTUM TRAINING")
