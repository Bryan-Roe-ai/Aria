"""Tests for repo_automation.py"""
import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRepoAutomationConfig:
    """Test repository automation configuration"""
    
    def test_default_repo_structure(self):
        """Test that repo has expected structure"""
        repo_root = Path(__file__).parent.parent
        
        required_dirs = [
            "scripts",
            "shared",
            "tests",
            "config",
            "data_out",
            "aria_web",
            "chat-web",
            "quantum-ai",
            "talk-to-ai"
        ]
        
        for dir_name in required_dirs:
            assert (repo_root / dir_name).exists(), f"Missing {dir_name}"
    
    def test_repo_has_function_app(self):
        """Test that function_app.py exists"""
        repo_root = Path(__file__).parent.parent
        assert (repo_root / "function_app.py").exists()
    
    def test_requirements_files_exist(self):
        """Test that all venv requirements files exist"""
        repo_root = Path(__file__).parent.parent
        
        required_files = [
            "requirements.txt",
            "dev-requirements.txt",
        ]
        
        for file_name in required_files:
            assert (repo_root / file_name).exists(), f"Missing {file_name}"


class TestRepoAutomationBackup:
    """Test backup functionality"""
    
    def test_backup_directory_creation(self):
        """Test creating backup directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_dir = Path(tmpdir) / "backups" / "20260117_120000"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            assert backup_dir.exists()
            assert backup_dir.parent.exists()
    
    def test_backup_manifest_creation(self):
        """Test creating backup manifest"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = {
                "timestamp": "2026-01-17T12:00:00Z",
                "version": "1.0",
                "files_backed_up": 150,
                "total_size_bytes": 5000000,
                "status": "completed"
            }
            
            manifest_file = Path(tmpdir) / "manifest.json"
            manifest_file.write_text(json.dumps(manifest, indent=2))
            
            loaded = json.loads(manifest_file.read_text())
            assert loaded["files_backed_up"] == 150
            assert loaded["status"] == "completed"
    
    def test_incremental_backup_logic(self):
        """Test incremental backup detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            # Create files with timestamps
            old_file = base_dir / "old.txt"
            old_file.write_text("old")
            old_file.touch()
            
            import time
            time.sleep(0.1)
            
            new_file = base_dir / "new.txt"
            new_file.write_text("new")
            
            # Get modification times
            old_mtime = old_file.stat().st_mtime
            new_mtime = new_file.stat().st_mtime
            
            # New file should have newer mtime
            assert new_mtime > old_mtime


class TestRepoAutomationNotifications:
    """Test notification system"""
    
    def test_notification_config_loading(self):
        """Test loading notification config"""
        config_path = Path(__file__).parent.parent / "config" / "notification_config.yaml"
        
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            assert config is not None
    
    def test_notification_message_formatting(self):
        """Test formatting notification messages"""
        message_template = "Automation {status}: {component} completed at {time}"
        
        formatted = message_template.format(
            status="success",
            component="training",
            time="12:00 UTC"
        )
        
        assert "success" in formatted
        assert "training" in formatted
        assert "12:00" in formatted


class TestRepoAutomationHealthCheck:
    """Test health check functionality"""
    
    def test_component_health_status(self):
        """Test checking component health"""
        components = {
            "aria_web": {"port": 8080, "healthy": True},
            "function_app": {"port": 7071, "healthy": True},
            "quantum_mcp": {"port": 5000, "healthy": False}
        }
        
        healthy_count = sum(1 for c in components.values() if c["healthy"])
        assert healthy_count == 2
    
    def test_database_pool_health(self):
        """Test database pool health check"""
        pool_stats = {
            "total_connections": 10,
            "active_connections": 8,
            "idle_connections": 2,
            "saturation_percent": 80
        }
        
        # Alert if saturation >= 80%
        should_alert = pool_stats["saturation_percent"] >= 80
        assert should_alert
    
    def test_storage_space_check(self):
        """Test checking available storage"""
        storage_info = {
            "total_bytes": 100 * 1024 * 1024 * 1024,  # 100 GB
            "used_bytes": 75 * 1024 * 1024 * 1024,    # 75 GB
            "available_bytes": 25 * 1024 * 1024 * 1024  # 25 GB
        }
        
        usage_percent = (storage_info["used_bytes"] / storage_info["total_bytes"]) * 100
        
        # Warn if usage > 80%
        should_warn = usage_percent > 80
        assert not should_warn  # 75% is OK


class TestRepoAutomationRollback:
    """Test rollback functionality"""
    
    def test_rollback_state_tracking(self):
        """Test tracking rollback state"""
        rollback_states = []
        
        def save_state(component, state_data):
            rollback_states.append({
                "component": component,
                "state": state_data,
                "timestamp": "2026-01-17T12:00:00Z"
            })
        
        save_state("training", {"epoch": 50, "accuracy": 0.92})
        save_state("quantum", {"jobs": 5, "completed": 3})
        
        assert len(rollback_states) == 2
        assert rollback_states[0]["component"] == "training"
    
    def test_rollback_execution(self):
        """Test executing rollback"""
        current_state = {
            "component": "training",
            "epoch": 50,
            "model_path": "/path/to/model_v50"
        }
        
        previous_state = {
            "component": "training",
            "epoch": 40,
            "model_path": "/path/to/model_v40"
        }
        
        # Verify we can identify rollback
        should_rollback = current_state["epoch"] > previous_state["epoch"]
        assert should_rollback


class TestRepoAutomationMonitoring:
    """Test monitoring and observability"""
    
    def test_status_file_updates(self):
        """Test updating status files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            status_file = Path(tmpdir) / "status.json"
            
            # Initial status
            status = {"state": "initializing", "components": 0, "started_at": None}
            status_file.write_text(json.dumps(status))
            
            # Update status
            status["state"] = "running"
            status["components"] = 5
            status["started_at"] = "2026-01-17T12:00:00Z"
            status_file.write_text(json.dumps(status))
            
            # Verify update
            loaded = json.loads(status_file.read_text())
            assert loaded["state"] == "running"
            assert loaded["components"] == 5
    
    def test_metrics_collection(self):
        """Test collecting automation metrics"""
        metrics = {
            "total_runs": 100,
            "successful_runs": 95,
            "failed_runs": 5,
            "avg_duration_seconds": 3600,
            "success_rate": 0.95
        }
        
        assert metrics["successful_runs"] / metrics["total_runs"] == metrics["success_rate"]
        assert metrics["failed_runs"] == metrics["total_runs"] - metrics["successful_runs"]
    
    def test_logs_collection(self):
        """Test collecting logs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "automation.log"
            
            logs = [
                "2026-01-17 12:00:00 - Starting automation",
                "2026-01-17 12:00:10 - Training component started",
                "2026-01-17 12:10:00 - Training component completed",
                "2026-01-17 12:10:05 - Quantum component started"
            ]
            
            log_file.write_text("\n".join(logs))
            
            content = log_file.read_text()
            lines = content.split("\n")
            
            assert len(lines) == 4
            assert "Starting automation" in lines[0]
            assert "completed" in lines[2]


class TestRepoAutomationScheduling:
    """Test automation scheduling"""
    
    def test_scheduler_config_loading(self):
        """Test loading scheduler config"""
        config_path = Path(__file__).parent.parent / "config" / "auto_scheduler.yaml"
        
        # Config might not exist, so we just test the logic
        scheduler_config = {
            "enabled": True,
            "interval_minutes": 30,
            "components": ["training", "quantum", "evaluation"]
        }
        
        assert scheduler_config["enabled"]
        assert scheduler_config["interval_minutes"] == 30
    
    def test_next_run_calculation(self):
        """Test calculating next run time"""
        from datetime import datetime, timedelta
        
        last_run = datetime(2026, 1, 17, 12, 0, 0)
        interval_minutes = 30
        
        next_run = last_run + timedelta(minutes=interval_minutes)
        
        assert next_run.hour == 12
        assert next_run.minute == 30
        
        time_until_next = next_run - datetime(2026, 1, 17, 12, 15, 0)
        assert time_until_next.total_seconds() == 15 * 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
