from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml


@pytest.mark.unit
def test_codeql_workflow_ignores_issue_template_changes() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "codeql.yml"
    assert workflow_path.exists(), "Expected CodeQL workflow to exist"

    workflow = yaml.load(workflow_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    assert ".github/ISSUE_TEMPLATE/**" in workflow["on"]["push"]["paths-ignore"]
    assert ".github/ISSUE_TEMPLATE/**" in workflow["on"]["pull_request"]["paths-ignore"]


@pytest.mark.unit
def test_codeql_autofix_ref_step_avoids_unbound_shell_vars() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "codeql.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert 'echo "ref=$ref_value"' not in content
    assert 'echo "repo=$repo_value"' not in content
    assert 'echo "can_push=$can_push_value"' not in content


@pytest.mark.unit
def test_codeql_autofix_excludes_workflow_files_from_formatting() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    workflow_path = repo_root / ".github" / "workflows" / "codeql.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "!**/.github/workflows/**" in content
    assert "!**/datasets/**" in content
    assert ":(exclude).github/workflows/**" in content

    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--",
            "*.c",
            "*.cc",
            "*.cpp",
            "*.cxx",
            "*.h",
            "*.hh",
            "*.hpp",
            "*.hxx",
            ":(exclude).github/workflows/**",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    files = result.stdout.splitlines()

    assert ".github/workflows/stdio.cpp" not in files
    assert "pxt_modules/base/advmath.cpp" in files


@pytest.mark.unit
def test_codeql_config_keeps_default_queries_for_autofix() -> None:
    config_path = Path(__file__).resolve().parents[1] / ".github" / "codeql" / "codeql-config.yml"
    assert config_path.exists(), "Expected CodeQL config to exist"

    config = yaml.load(config_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    assert config.get("disable-default-queries") == "false"
    assert "**/fixtures/**" in config["paths-ignore"]


@pytest.mark.unit
def test_codeql_config_has_document_start_and_no_trailing_whitespace() -> None:
    config_path = Path(__file__).resolve().parents[1] / ".github" / "codeql" / "codeql-config.yml"
    content = config_path.read_text(encoding="utf-8")

    assert content.startswith("---\n")
    assert all(line == line.rstrip() for line in content.splitlines())
