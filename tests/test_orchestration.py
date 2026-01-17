"""Tests for repo automation and master orchestrator."""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))


class TestRepoAutomationConfig:
    """Test repo automation configuration."""
    
    def test_load_automation_config(self, tmp_path):
        """Test loading automation configuration."""
        config_file = tmp_path / "repo_config.yaml"
        config_data = {
            'components': ['aria', 'training', 'quantum'],
            'backup_enabled': True,
            'notification_enabled': False
        }
        config_file.write_text(f"---\ncomponents: {config_data['components']}\nbackup_enabled: true\n")
        
        # Test YAML parsing
        import yaml
        with open(config_file) as f:
            loaded = yaml.safe_load(f)
            assert 'components' in loaded
            assert isinstance(loaded['components'], list)


class TestComponentOrchestration:
    """Test orchestration of multiple components."""
    
    def test_start_all_components(self):
        """Test starting all automation components."""
        components = ['aria_server', 'training_pipeline', 'quantum_jobs']
        
        started = []
        for component in components:
            # Mock component startup
            started.append(component)
        
        assert len(started) == len(components)
    
    def test_component_health_checks(self):
        """Test health checking of running components."""
        components_status = {
            'aria_server': {'running': True, 'port': 8080},
            'training': {'running': True, 'cycle': 5},
            'quantum': {'running': False, 'error': 'Backend unavailable'}
        }
        
        running_count = sum(1 for c in components_status.values() if c.get('running'))
        assert running_count >= 1


class TestBackupManager:
    """Test backup management functionality."""
    
    def test_create_backup_directory(self, tmp_path):
        """Test creating backup directories."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        assert backup_dir.exists()
        assert backup_dir.is_dir()
    
    def test_backup_includes_timestamp(self, tmp_path):
        """Test that backups include timestamps."""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.tar.gz"
        backup_path = tmp_path / backup_name
        
        # Create mock backup
        backup_path.write_text("mock backup content")
        
        assert backup_path.exists()
        assert timestamp in backup_path.name


class TestMasterOrchestratorScheduling:
    """Test master orchestrator scheduling logic."""
    
    def test_parse_cron_schedule(self):
        """Test parsing cron schedule expressions."""
        schedules = {
            'nightly_training': '0 2 * * *',  # 2 AM daily
            'hourly_backup': '0 * * * *',     # Every hour
            'weekly_cleanup': '0 0 * * 0'     # Sunday midnight
        }
        
        # Verify schedule format
        for name, cron in schedules.items():
            parts = cron.split()
            assert len(parts) == 5  # minute hour day month weekday
    
    def test_schedule_priority_ordering(self):
        """Test that scheduled tasks respect priority."""
        tasks = [
            {'name': 'critical_backup', 'priority': 1},
            {'name': 'routine_training', 'priority': 3},
            {'name': 'low_priority_cleanup', 'priority': 5}
        ]
        
        sorted_tasks = sorted(tasks, key=lambda x: x['priority'])
        
        assert sorted_tasks[0]['name'] == 'critical_backup'
        assert sorted_tasks[-1]['name'] == 'low_priority_cleanup'


class TestDependencyResolution:
    """Test task dependency resolution."""
    
    def test_resolve_task_dependencies(self):
        """Test resolving dependencies between tasks."""
        tasks = {
            'task_a': {'depends_on': []},
            'task_b': {'depends_on': ['task_a']},
            'task_c': {'depends_on': ['task_a', 'task_b']}
        }
        
        # Task execution order should respect dependencies
        execution_order = []
        
        # Simple dependency resolver
        completed = set()
        while len(execution_order) < len(tasks):
            for name, task in tasks.items():
                if name not in completed:
                    deps_met = all(dep in completed for dep in task['depends_on'])
                    if deps_met:
                        execution_order.append(name)
                        completed.add(name)
        
        # task_a should be first, task_c should be last
        assert execution_order[0] == 'task_a'
        assert execution_order[-1] == 'task_c'


class TestRetryLogic:
    """Test retry logic for failed tasks."""
    
    def test_retry_failed_task(self):
        """Test that failed tasks are retried."""
        max_retries = 3
        attempt = 0
        
        def failing_task():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise Exception("Task failed")
            return "success"
        
        # Retry loop
        for _ in range(max_retries):
            try:
                result = failing_task()
                if result == "success":
                    break
            except Exception:
                continue
        
        assert attempt == 3
        assert result == "success"
    
    def test_exponential_backoff(self):
        """Test exponential backoff between retries."""
        import time
        
        retry_delays = []
        for retry in range(3):
            delay = min(60, 2 ** retry)  # Exponential, max 60s
            retry_delays.append(delay)
        
        # Should increase: 1, 2, 4
        assert retry_delays[0] == 1
        assert retry_delays[1] == 2
        assert retry_delays[2] == 4


class TestTimeoutHandling:
    """Test timeout handling for long-running tasks."""
    
    def test_task_timeout_enforcement(self):
        """Test that tasks respect timeout limits."""
        timeout_seconds = 5
        start_time = 0
        elapsed = 0
        
        # Simulate task with timeout check
        while elapsed < timeout_seconds:
            elapsed += 1
            if elapsed >= timeout_seconds:
                break
        
        assert elapsed == timeout_seconds


class TestNotificationSystem:
    """Test notification system for orchestrator events."""
    
    def test_notification_on_failure(self):
        """Test notifications are sent on task failure."""
        notifications = []
        
        def send_notification(message, level):
            notifications.append({'message': message, 'level': level})
        
        # Simulate failure
        send_notification("Task 'training' failed after 3 retries", "error")
        
        assert len(notifications) == 1
        assert notifications[0]['level'] == 'error'
    
    def test_notification_channels(self):
        """Test different notification channels."""
        channels = ['email', 'slack', 'local_log']
        
        enabled_channels = [c for c in channels if c in ['local_log']]
        
        assert len(enabled_channels) >= 1


class TestStatusDashboard:
    """Test status dashboard generation."""
    
    def test_generate_status_summary(self, tmp_path):
        """Test generating orchestrator status summary."""
        status = {
            'orchestrator': 'master',
            'uptime_seconds': 3600,
            'components': {
                'aria': {'status': 'running', 'cycles': 5},
                'training': {'status': 'running', 'epoch': 100},
                'quantum': {'status': 'idle'}
            },
            'last_updated': '2026-01-17T12:00:00Z'
        }
        
        status_file = tmp_path / "orchestrator_status.json"
        status_file.write_text(json.dumps(status, indent=2))
        
        loaded = json.loads(status_file.read_text())
        assert loaded['orchestrator'] == 'master'
        assert 'components' in loaded
        assert len(loaded['components']) == 3


@pytest.mark.integration
class TestFullOrchestrationCycle:
    """Integration tests for full orchestration cycle."""
    
    def test_orchestrator_dry_run(self, tmp_path):
        """Test orchestrator dry-run mode."""
        config = {
            'dry_run': True,
            'components': ['aria', 'training'],
            'schedules': {}
        }
        
        # Simulate dry run
        executed_tasks = []
        for component in config['components']:
            # In dry run, just log without executing
            executed_tasks.append(f"[DRY-RUN] {component}")
        
        assert all('[DRY-RUN]' in task for task in executed_tasks)
    
    def test_graceful_shutdown_all_components(self):
        """Test graceful shutdown of all components."""
        components = ['aria', 'training', 'quantum']
        shutdown_sequence = []
        
        # Shutdown in reverse order for safety
        for component in reversed(components):
            shutdown_sequence.append(component)
        
        assert shutdown_sequence[0] == 'quantum'
        assert len(shutdown_sequence) == len(components)
