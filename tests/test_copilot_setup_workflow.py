from __future__ import annotations

from pathlib import Path

import pytest
import yaml


def _read_copilot_setup_workflow() -> str:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "copilot-setup-steps.yml"
    assert workflow_path.exists(), "Expected copilot setup workflow to exist"
    return workflow_path.read_text(encoding="utf-8")


def _workflow_step_by_name(steps: list[dict[str, object]], name: str) -> dict[str, object]:
    for step in steps:
        if step.get("name") == name:
            return step
    raise AssertionError(f"Expected workflow step named {name!r}")


@pytest.mark.unit
def test_copilot_setup_workflow_concurrency_is_ref_scoped() -> None:
    content = _read_copilot_setup_workflow()

    assert "concurrency:" in content
    assert "group: copilot-setup-check-${{ github.event.pull_request.number || github.ref }}" in content


@pytest.mark.unit
def test_copilot_setup_workflow_has_selective_lint_logic() -> None:
    content = _read_copilot_setup_workflow()

    assert "fetch-depth: 50" in content
    assert "id: targets" in content
    assert "NULL_SHA=" in content
    assert "git diff --name-only" in content
    assert "--diff-filter=ACMR -z" in content
    assert "load_changed_targets() {" in content
    assert 'load_changed_targets "${PR_BASE_SHA}" "${PR_HEAD_SHA}" || load_default_targets' in content
    assert 'load_changed_targets "${PUSH_BEFORE_SHA}" "${HEAD_SHA}" || load_default_targets' in content
    assert 'YAML_LIST_FILE="${{ steps.targets.outputs.yaml_list_file }}"' in content
    assert 'MD_LIST_FILE="${{ steps.targets.outputs.md_list_file }}"' in content
    assert "is_markdown_target() {" in content
    assert 'case "$rel" in' in content
    assert "*/*)" in content
    assert "COPILOT*.md|copilot-*.md" in content
    assert "find .github -maxdepth 1 -type f \\( -name 'COPILOT*.md' -o -name 'copilot-*.md' \\)" in content
    assert 'is_markdown_target "$file" && printf \'%s\\0\' "$file" >> "$MD_LIST_FILE"' in content


@pytest.mark.unit
def test_copilot_setup_workflow_hardening_contract() -> None:
    content = _read_copilot_setup_workflow()
    workflow = yaml.safe_load(content)
    setup_steps = workflow["jobs"]["validate-setup"]["steps"]
    harden_runner_step = _workflow_step_by_name(setup_steps, "Harden runner")
    setup_node_step = _workflow_step_by_name(setup_steps, "Setup Node")
    setup_python_step = _workflow_step_by_name(setup_steps, "Setup Python")

    assert "runs-on: ubuntu-24.04" in content
    assert "egress-policy: block" in content
    assert harden_runner_step["with"]["allowed-endpoints"].split() == [
        "github.com:443",
        "api.github.com:443",
        "objects.githubusercontent.com:443",
        "pypi.org:443",
        "files.pythonhosted.org:443",
        "registry.npmjs.org:443",
    ]
    assert "cache: 'npm'" in content
    assert "cache: 'pip'" in content
    assert setup_node_step["with"]["cache-dependency-path"] == ".github/workflows/copilot-setup-steps.yml"
    assert setup_python_step["with"]["cache-dependency-path"] == ".github/workflows/copilot-setup-steps.yml"
    assert "yamllint -c .github/yamllint.yml" in content
    assert "YAML_OUTCOME: ${{ steps.yamllint.outcome }}" in content
    assert "MD_OUTCOME: ${{ steps.mdlint.outcome }}" in content
    assert 'echo "yamllint outcome: $YAML_OUTCOME"' in content
    assert 'echo "markdownlint outcome: $MD_OUTCOME"' in content
    assert "# Requires bash 4+ for associative arrays." in content

    assert content.startswith("name: Copilot setup validation\n")
    name_idx = 0
    on_idx = content.index("\non:")
    permissions_idx = content.index("\npermissions:")
    concurrency_idx = content.index("\nconcurrency:")
    env_idx = content.index("\nenv:")
    jobs_idx = content.index("\njobs:")
    assert name_idx < on_idx < permissions_idx < concurrency_idx < env_idx < jobs_idx


@pytest.mark.unit
def test_copilot_setup_yamllint_config_matches_expected_rules() -> None:
    config_path = Path(__file__).resolve().parents[1] / ".github" / "yamllint.yml"
    assert config_path.exists(), "Expected .github/yamllint.yml to exist"

    assert yaml.safe_load(config_path.read_text(encoding="utf-8")) == {
        "extends": "default",
        "rules": {"line-length": {"max": 140, "level": "warning"}},
    }


@pytest.mark.unit
def test_copilot_entrypoint_files_exist_and_reference_instructions() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    copilot_md = repo_root / ".github" / "COPILOT.md"
    copilot_yml = repo_root / ".github" / "copilot.yml"

    assert copilot_md.exists(), "Expected .github/COPILOT.md to exist"
    assert copilot_yml.exists(), "Expected .github/copilot.yml to exist"
    assert (repo_root / ".github" / "copilot-instructions.md").exists()
    assert (repo_root / ".github" / "copilot-instructions.full.md").exists()
    assert (repo_root / ".github" / "COPILOT_SETUP_GUIDE.md").exists()

    copilot_md_content = copilot_md.read_text(encoding="utf-8")
    assert ".github/copilot-instructions.md" in copilot_md_content
    assert ".github/copilot-instructions.full.md" in copilot_md_content

    copilot_yml_content = copilot_yml.read_text(encoding="utf-8")
    assert "quick_instructions" in copilot_yml_content
    assert "full_instructions" in copilot_yml_content
    assert "setup_guide" in copilot_yml_content
    assert ".github/copilot-instructions.md" in copilot_yml_content
    assert ".github/copilot-instructions.full.md" in copilot_yml_content
    assert ".github/COPILOT_SETUP_GUIDE.md" in copilot_yml_content
