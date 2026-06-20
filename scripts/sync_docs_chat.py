#!/usr/bin/env python3
"""Sync apps/chat assets into docs/chat for GitHub Pages parity."""

from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "apps" / "chat"
DST = REPO_ROOT / "docs" / "chat"


def sync_docs_chat() -> None:
    """Copy chat.js and AGI stream utilities into docs/chat."""
    DST.mkdir(parents=True, exist_ok=True)
    static_dst = DST / "static"
    static_dst.mkdir(parents=True, exist_ok=True)

    shutil.copy2(SRC / "chat.js", DST / "chat.js")
    shutil.copy2(SRC / "static" / "agi_stream_utils.js", static_dst / "agi_stream_utils.js")


def main() -> int:
    sync_docs_chat()
    print(f"Synced chat assets: {SRC} -> {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
