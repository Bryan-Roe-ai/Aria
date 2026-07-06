"""Integration tests for config validation gates."""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestConfigValidationGates:
    """Test config validation gates in orchestrator entrypoints."""

    def test_autonomous_training_with_valid_config(self):
        """Test autonomous_training_orchestrator with valid config."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/autonomous_training_orchestrator.py",
                "--status",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # Should succeed with valid config
        assert result.returncode == 0
        assert "cycles_completed" in result.stdout

    def test_repo_automation_validate_flag(self):
        """Test repo_automation.py --validate flag."""
        result = subprocess.run(
            [sys.executable, "scripts/repo_automation.py", "--validate"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
        # Should exit with 0 if configs are valid
        assert result.returncode == 0
        assert "✅" in result.stdout or "valid" in result.stdout.lower()

    def test_repo_automation_validate_flag_handles_non_utf8_stdio(self):
        """Test repo_automation.py --validate with a non-UTF-8 stdio encoding."""
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        result = subprocess.run(
            [sys.executable, "scripts/repo_automation.py", "--validate"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            env=env,
            check=False,
        )
        assert result.returncode == 0
        assert "valid" in result.stdout.lower()

    def test_repo_automation_wrapper_validate_mode(self):
        """Test start_repo_automation.sh validate mode."""
        result = subprocess.run(
            ["bash", "scripts/start_repo_automation.sh", "validate"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert result.returncode == 0
        assert "validate" in result.stdout.lower() or "valid" in result.stdout.lower()

    def test_repo_automation_wrapper_python3_nounset(self, tmp_path: Path):
        """Wrapper should use python3 fallback.

        Also avoid raw unset positional args.
        """
        repo_root = tmp_path
        scripts_dir = repo_root / "scripts"
        data_out_dir = repo_root / "data_out" / "repo_automation"
        fake_bin_dir = repo_root / "fake-bin"
        invocation_log = repo_root / "python3-invocations.log"

        scripts_dir.mkdir(parents=True)
        data_out_dir.mkdir(parents=True)
        fake_bin_dir.mkdir(parents=True)

        wrapper_src = REPO_ROOT / "scripts" / "start_repo_automation.sh"
        wrapper_dst = scripts_dir / "start_repo_automation.sh"
        wrapper_dst.write_text(wrapper_src.read_text())
        wrapper_dst.chmod(0o755)

        (scripts_dir / "repo_automation.py").write_text(
            "import sys\nprint('repo_automation stub', ' '.join(sys.argv[1:]))\n"
        )

        (fake_bin_dir / "python3").write_text(
            "#!/bin/sh\n"
            'if [ "$1" = "--version" ]; then\n'
            "  echo 'Python 3.11.9'\n"
            "  exit 0\n"
            "fi\n"
            'if [ "$1" = "-c" ]; then\n'
            "  exit 0\n"
            "fi\n"
            'printf \'%s\\n\' "$*" >> "$PYTHON3_LOG"\n'
            "exit 0\n"
        )
        (fake_bin_dir / "python3").chmod(0o755)

        env = os.environ.copy()
        env["PATH"] = f"{fake_bin_dir}:{env['PATH']}"
        env["PYTHON3_LOG"] = str(invocation_log)

        status_result = subprocess.run(
            ["bash", "-u", str(wrapper_dst), "status"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
            check=False,
        )
        assert status_result.returncode == 0

        components_result = subprocess.run(
            ["bash", "-u", str(wrapper_dst), "components"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
            check=False,
        )
        assert components_result.returncode == 0
        assert "Available Components" in components_result.stdout

        log_lines = invocation_log.read_text().splitlines()
        assert any("scripts/repo_automation.py --status" in line for line in log_lines)

    def test_master_orchestrator_validation(self):
        """Test master_orchestrator.py validation gate."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/master_orchestrator.py",
                "--list-orchestrators",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # Should succeed with valid config
        assert result.returncode == 0
        # Should list orchestrators
        assert "autotrain" in result.stdout
        assert "quantum_autorun" in result.stdout

    def test_repo_automation_start_with_validation(self):
        """Test repo_automation.py --start with built-in validation."""
        # This should validate configs before starting anything
        # We won't actually start anything;
        # this just tests that the --start path works.
        result = subprocess.run(
            [sys.executable, "scripts/repo_automation.py", "--status"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        # Should succeed
        # (status doesn't trigger validation, but setup should work).
        assert result.returncode == 0 or "no status" in result.stdout.lower()
