#!/usr/bin/env python3
"""Backward-compatible entrypoint for tools/codegen/code_generation_quickstart.py."""

import runpy
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
codegen_dir = repo_root / "tools" / "codegen"
sys.path.insert(0, str(codegen_dir))
runpy.run_path(str(codegen_dir / "code_generation_quickstart.py"), run_name="__main__")
