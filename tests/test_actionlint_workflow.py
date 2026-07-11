from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def test_actionlint_shellcheck_ignores_vendored_dotnet_script() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "actionlint.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    shellcheck_step = next(
        step for step in workflow["jobs"]["actionlint"]["steps"] if step.get("name") == "Setup ShellCheck (pinned)"
    )

    ignore_paths = shellcheck_step["with"]["ignore_paths"].split()
    assert "*/dotnet-install.sh" in ignore_paths
