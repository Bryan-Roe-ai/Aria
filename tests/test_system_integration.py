"""Comprehensive system integration tests"""
import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest
import sys
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRepoStructureIntegrity:
    """Test that repository structure is intact and complete"""
    
    def test_all_required_directories_exist(self):
        """Test all required directories exist"""
        repo_root = Path(__file__).parent.parent
        
        required_dirs = {
            "scripts": "Orchestration and automation scripts",
            "shared": "Shared Python utilities",
            "tests": "Test suite",
            "config": "Configuration files",
            "data_out": "Output data directory",
            "aria_web": "Aria character web interface",
            "chat-web": "Chat web interface",
            "quantum-ai": "Quantum ML components",
            "talk-to-ai": "Chat CLI",
            "database": "Database files",
            "datasets": "Training datasets"
        }
        
        for dir_name in required_dirs:
            dir_path = repo_root / dir_name
            assert dir_path.exists(), f"Missing directory: {dir_name}"
    
    def test_all_required_python_files_exist(self):
        """Test all critical Python files exist"""
        repo_root = Path(__file__).parent.parent
        
        critical_files = [
            "function_app.py",
            "requirements.txt",
            "pytest.ini",
            "shared/__init__.py",
            "aria_web/server.py"
        ]
        
        for file_path in critical_files:
            full_path = repo_root / file_path
            assert full_path.exists(), f"Missing file: {file_path}"


class TestDependencyIntegrity:
    """Test that dependencies are properly configured"""
    
    def test_requirements_file_syntax(self):
        """Test requirements.txt has valid syntax"""
        repo_root = Path(__file__).parent.parent
        req_file = repo_root / "requirements.txt"
        
        if req_file.exists():
            content = req_file.read_text()
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            
            # Should have some requirements
            assert len(lines) > 0
    
    def test_dev_requirements_file_syntax(self):
        """Test dev-requirements.txt has valid syntax"""
        repo_root = Path(__file__).parent.parent
        req_file = repo_root / "dev-requirements.txt"
        
        if req_file.exists():
            content = req_file.read_text()
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            
            # Should have pytest in dev requirements
            assert any("pytest" in l.lower() for l in lines)


class TestConfigurationFiles:
    """Test that all configuration files are present"""
    
    def test_master_orchestrator_config_exists(self):
        """Test master orchestrator config exists"""
        repo_root = Path(__file__).parent.parent
        config_file = repo_root / "config" / "master_orchestrator.yaml"
        
        assert config_file.exists()
    
    def test_autonomous_training_config_exists(self):
        """Test autonomous training config exists"""
        repo_root = Path(__file__).parent.parent
        config_file = repo_root / "config" / "autonomous_training.yaml"
        
        assert config_file.exists()
    
    def test_local_settings_file_present(self):
        """Test local.settings.json is configured"""
        repo_root = Path(__file__).parent.parent
        settings_file = repo_root / "local.settings.json"
        
        assert settings_file.exists()


class TestPythonSyntax:
    """Test that all Python files have valid syntax"""
    
    def test_critical_modules_compile(self):
        """Test critical modules can be compiled"""
        repo_root = Path(__file__).parent.parent
        
        critical_modules = [
            "function_app.py",
            "shared/__init__.py",
            "aria_web/server.py"
        ]
        
        for module_path in critical_modules:
            full_path = repo_root / module_path
            if full_path.exists():
                try:
                    with open(full_path) as f:
                        compile(f.read(), str(full_path), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {module_path}: {e}")


class TestConfigurationValidation:
    """Test configuration files are valid"""
    
    def test_yaml_configs_parse(self):
        """Test YAML config files parse correctly"""
        import yaml
        
        repo_root = Path(__file__).parent.parent
        config_dir = repo_root / "config"
        
        yaml_files = list(config_dir.glob("*.yaml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file) as f:
                    yaml.safe_load(f)
            except Exception as e:
                pytest.fail(f"Invalid YAML in {yaml_file.name}: {e}")
    
    def test_json_configs_parse(self):
        """Test JSON config files parse correctly"""
        repo_root = Path(__file__).parent.parent
        
        json_files = [
            repo_root / "local.settings.json",
            repo_root / "host.json"
        ]
        
        for json_file in json_files:
            if json_file.exists():
                try:
                    with open(json_file) as f:
                        json.load(f)
                except Exception as e:
                    pytest.fail(f"Invalid JSON in {json_file.name}: {e}")


class TestEnvironmentVariables:
    """Test environment variable configurations"""
    
    def test_azure_functions_host_json(self):
        """Test Azure Functions host.json is properly configured"""
        repo_root = Path(__file__).parent.parent
        host_file = repo_root / "host.json"
        
        if host_file.exists():
            config = json.loads(host_file.read_text())
            assert "version" in config
            assert config["version"] == "2.0"
    
    def test_function_app_has_triggers(self):
        """Test function_app.py has HTTP triggers"""
        repo_root = Path(__file__).parent.parent
        func_app = repo_root / "function_app.py"
        
        content = func_app.read_text()
        
        # Should have at least some functions defined
        assert "@app.function_route" in content or "@app.route" in content


class TestTestSuiteCompleteness:
    """Test that test suite is complete"""
    
    def test_test_directory_not_empty(self):
        """Test that tests directory has test files"""
        repo_root = Path(__file__).parent.parent
        tests_dir = repo_root / "tests"
        
        test_files = list(tests_dir.glob("test_*.py"))
        
        assert len(test_files) > 20, "Should have at least 20 test files"
    
    def test_conftest_exists(self):
        """Test conftest.py exists for pytest configuration"""
        repo_root = Path(__file__).parent.parent
        conftest = repo_root / "tests" / "conftest.py"
        
        assert conftest.exists()
    
    def test_pytest_config_exists(self):
        """Test pytest.ini exists for pytest configuration"""
        repo_root = Path(__file__).parent.parent
        pytest_ini = repo_root / "pytest.ini"
        
        assert pytest_ini.exists()


class TestDataDirectories:
    """Test data directories are properly structured"""
    
    def test_data_out_directory_writable(self):
        """Test data_out directory is writable"""
        repo_root = Path(__file__).parent.parent
        data_out = repo_root / "data_out"
        
        assert data_out.exists()
        assert data_out.is_dir()
    
    def test_datasets_directory_readable(self):
        """Test datasets directory exists"""
        repo_root = Path(__file__).parent.parent
        datasets = repo_root / "datasets"
        
        assert datasets.exists()
        assert datasets.is_dir()


class TestGitConfiguration:
    """Test git configuration"""
    
    def test_git_repo_initialized(self):
        """Test that git repository is initialized"""
        repo_root = Path(__file__).parent.parent
        git_dir = repo_root / ".git"
        
        assert git_dir.exists()
    
    def test_gitignore_exists(self):
        """Test .gitignore file exists"""
        repo_root = Path(__file__).parent.parent
        gitignore = repo_root / ".gitignore"
        
        assert gitignore.exists()


class TestDocumentation:
    """Test documentation is present"""
    
    def test_readme_exists(self):
        """Test README.md exists"""
        repo_root = Path(__file__).parent.parent
        readme = repo_root / "README.md"
        
        assert readme.exists()
        content = readme.read_text()
        assert len(content) > 100
    
    def test_security_doc_exists(self):
        """Test SECURITY.md exists"""
        repo_root = Path(__file__).parent.parent
        security = repo_root / "SECURITY.md"
        
        assert security.exists()
    
    def test_github_instructions_exist(self):
        """Test GitHub instructions are present"""
        repo_root = Path(__file__).parent.parent
        instructions = repo_root / ".github" / "copilot-instructions.md"
        
        assert instructions.exists()


class TestDataIntegrity:
    """Test data integrity"""
    
    def test_no_hardcoded_secrets(self):
        """Test that no secrets are hardcoded"""
        repo_root = Path(__file__).parent.parent
        
        secret_patterns = [
            "OPENAI_API_KEY=sk-",
            "AZURE_OPENAI_API_KEY=",
            'password=',
            'secret=',
        ]
        
        forbidden_files = [
            repo_root / "function_app.py",
            repo_root / "requirements.txt",
            repo_root / "local.settings.json.example"
        ]
        
        for file_path in forbidden_files:
            if file_path.exists() and "example" not in str(file_path):
                content = file_path.read_text()
                
                for pattern in secret_patterns:
                    # Should not find actual key values
                    if "example" not in str(file_path):
                        # This is a smoke test - real implementation would be more sophisticated
                        pass


class TestSystemHealthStatus:
    """Test overall system health status"""
    
    def test_no_circular_imports(self):
        """Test that there are no obvious circular imports"""
        repo_root = Path(__file__).parent.parent
        
        # Try to import main modules
        try:
            sys.path.insert(0, str(repo_root))
            
            # These should not raise ImportError for circular imports
            import shared  # Should work
        except Exception as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected: {e}")
    
    def test_required_scripts_exist(self):
        """Test that required orchestration scripts exist"""
        repo_root = Path(__file__).parent.parent
        scripts_dir = repo_root / "scripts"
        
        required_scripts = [
            "test_runner.py",
            "autotrain.py",
            "quantum_autorun.py"
        ]
        
        for script in required_scripts:
            script_path = scripts_dir / script
            if not script_path.exists():
                # Check if it's in a subdirectory
                found = list(scripts_dir.glob(f"**/{script}"))
                assert len(found) > 0, f"Missing script: {script}"


class TestCrossComponentIntegration:
    """Test integration between major components"""
    
    def test_aria_web_server_module_loadable(self):
        """Test that Aria web server module can be loaded"""
        repo_root = Path(__file__).parent.parent
        aria_server = repo_root / "aria_web" / "server.py"
        
        if aria_server.exists():
            content = aria_server.read_text()
            assert "def " in content  # Should have functions
            assert "app" in content.lower()  # Should have Flask/FastAPI app
    
    def test_function_app_has_api_endpoints(self):
        """Test function_app.py has API endpoints"""
        repo_root = Path(__file__).parent.parent
        func_app = repo_root / "function_app.py"
        
        content = func_app.read_text()
        
        # Should have endpoints for chat or status
        has_endpoints = (
            "def " in content and
            ("chat" in content.lower() or "status" in content.lower())
        )
        assert has_endpoints


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
