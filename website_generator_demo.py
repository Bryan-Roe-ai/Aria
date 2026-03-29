#!/usr/bin/env python3
"""Backward-compatible entrypoint for tools/codegen/website_generator_demo.py."""

from pathlib import Path
import sys
import runpy

codegen_dir = Path(__file__).parent / "tools" / "codegen"
sys.path.insert(0, str(codegen_dir))
runpy.run_path(str(codegen_dir / "website_generator_demo.py"), run_name="__main__")
