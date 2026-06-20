from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


@pytest.mark.unit
def test_mount_app_loads_with_repo_layout() -> None:
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    mount_dir = repo_root / "mount"
    app_path = mount_dir / "app.py"

    mount_path = str(mount_dir)
    added_to_path = False
    if mount_path not in sys.path:
        sys.path.insert(0, mount_path)
        added_to_path = True

    spec = importlib.util.spec_from_file_location("qai_mount_app_under_test", app_path)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        if added_to_path:
            sys.path.remove(mount_path)

    assert module.app.title == "QAI Integration Service"
    assert module.config["paths"]["workspace_root"] == str(repo_root)
    assert module.config["paths"]["quantum_ai"] == str(repo_root / "ai-projects" / "quantum-ml")
    assert module.config["paths"]["talk_to_ai"] == str(repo_root / "ai-projects" / "chat-cli")
    assert module.chat_integration.chat_path == repo_root / "ai-projects" / "chat-cli"
