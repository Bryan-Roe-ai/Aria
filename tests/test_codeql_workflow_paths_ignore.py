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
def test_codeql_autofix_uses_sha_for_checkout_and_branch_for_push() -> None:
    """Verify the autofix job uses SHA for checkout (resilient to branch deletion)
    and a separate push_ref for the git push step (uses branch name)."""
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "codeql.yml"
    content = workflow_path.read_text(encoding="utf-8")

    # The "Determine checkout ref" step must expose PR_HEAD_SHA for checkout
    assert "PR_HEAD_SHA" in content, "PR_HEAD_SHA env var must be set in the ref step"
    assert 'echo "ref=$PR_HEAD_SHA"' in content, "checkout ref must use SHA, not branch name"
    assert 'echo "push_ref=$PR_HEAD_REF"' in content, "push_ref must preserve the branch name"

    # The push step must use push_ref (branch name), not ref (SHA)
    assert "steps.ref.outputs.push_ref" in content, "git push must target push_ref (branch name)"
    # push_ref is surfaced via PUSH_REF env var to keep shell script clean
    assert "PUSH_REF: ${{ steps.ref.outputs.push_ref }}" in content, "PUSH_REF env var must map push_ref"
    assert "HEAD:$PUSH_REF" in content, "push must use PUSH_REF env var (branch name)"


@pytest.mark.unit
def test_codeql_autofix_excludes_workflow_files_from_formatting() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    workflow_path = repo_root / ".github" / "workflows" / "codeql.yml"
    content = workflow_path.read_text(encoding="utf-8")

    assert "!**/.github/workflows/**" in content
    assert "!**/datasets/**" in content
    assert ":(exclude).github/workflows/**" in content
    assert "git restore --staged --worktree -- .github/workflows" in content

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

    assert content.startswith("---\n"), "CodeQL config must keep its YAML document start marker."
    assert all(line == line.rstrip() for line in content.splitlines()), (
        "CodeQL config should not contain trailing whitespace."
    )
