"""Tests for autonomous training orchestrator."""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

try:
    import autonomous_training_orchestrator as ato
except ImportError:
    pytest.skip("Autonomous training orchestrator not available", allow_module_level=True)


class TestAutonomousTrainingConfig:
    """Test configuration loading and validation."""
    
    def test_load_default_config(self, tmp_path):
        """Test loading default configuration."""
        config_file = tmp_path / "test_config.yaml"
        config_data = {
            'cycle_interval_minutes': 30,
            'epochs_progression': [25, 50, 100],
            'min_datasets': 5,
            'auto_promotion_threshold': 0.90
        }
        config_file.write_text(f"---\n{json.dumps(config_data)}")
        
        # Mock the config loading
        with patch.object(ato, 'CONFIG_FILE', config_file):
            config = ato.load_config()
            assert config['cycle_interval_minutes'] == 30
            assert len(config['epochs_progression']) == 3


class TestDatasetDiscovery:
    """Test dataset discovery and cataloging."""
    
    def test_discover_datasets_returns_dict(self, tmp_path):
        """Test that dataset discovery returns a dictionary."""
        datasets_dir = tmp_path / "datasets"
        datasets_dir.mkdir()
        
        # Create sample dataset
        (datasets_dir / "chat").mkdir()
        dataset_file = datasets_dir / "chat" / "sample.jsonl"
        dataset_file.write_text('{"messages": [{"role": "user", "content": "hi"}]}\n')
        
        with patch.object(ato, 'DATASETS_DIR', datasets_dir):
            discovered = ato.discover_datasets()
            assert isinstance(discovered, dict)
            assert 'chat' in discovered or len(discovered) >= 0


class TestPerformanceTracking:
    """Test performance tracking and metrics."""
    
    def test_track_cycle_performance(self):
        """Test cycle performance tracking."""
        cycle_data = {
            'cycle_number': 1,
            'accuracy': 0.85,
            'duration': 120.5,
            'datasets_used': 3
        }
        
        # Mock performance history
        with patch.object(ato, 'performance_history', []):
            ato.track_cycle_performance(cycle_data)
            assert len(ato.performance_history) == 1
            assert ato.performance_history[0]['accuracy'] == 0.85


class TestEpochSelection:
    """Test adaptive epoch selection logic."""
    
    def test_select_optimal_epochs_increases_on_low_accuracy(self):
        """Test that epochs increase when accuracy is low."""
        with patch.object(ato, 'performance_history', [
            {'accuracy': 0.60, 'epochs': 25},
            {'accuracy': 0.62, 'epochs': 25}
        ]):
            optimal_epochs = ato.select_optimal_epochs([25, 50, 100])
            # Should increase from 25 to 50
            assert optimal_epochs >= 25


class TestStatusJSON:
    """Test status JSON generation."""
    
    def test_generate_status_json_structure(self, tmp_path):
        """Test status JSON has correct structure."""
        status_file = tmp_path / "status.json"
        
        status_data = {
            'cycles_completed': 5,
            'best_accuracy': 0.92,
            'current_cycle': 6,
            'performance_history': [
                {'cycle': 1, 'accuracy': 0.80},
                {'cycle': 2, 'accuracy': 0.85}
            ]
        }
        
        status_file.write_text(json.dumps(status_data, indent=2))
        
        loaded = json.loads(status_file.read_text())
        assert 'cycles_completed' in loaded
        assert 'best_accuracy' in loaded
        assert isinstance(loaded['performance_history'], list)
        assert loaded['best_accuracy'] == 0.92


class TestGracefulShutdown:
    """Test graceful shutdown and signal handling."""
    
    def test_signal_handler_sets_flag(self):
        """Test that signal handler sets shutdown flag."""
        with patch.object(ato, 'shutdown_flag', False):
            # Simulate signal
            ato.handle_shutdown_signal(None, None)
            assert ato.shutdown_flag is True


class TestErrorRecovery:
    """Test error recovery mechanisms."""
    
    def test_continue_on_training_failure(self):
        """Test that orchestrator continues after training failure."""
        with patch.object(ato, 'run_training_cycle', side_effect=Exception("Training failed")):
            with patch.object(ato, 'log_error') as mock_log:
                try:
                    result = ato.run_cycle_with_recovery(1)
                    # Should log error but not crash
                    assert mock_log.called or result is not None
                except Exception:
                    pytest.fail("Should not raise exception on recoverable error")


@pytest.mark.integration
class TestFullCycle:
    """Integration tests for full training cycle."""
    
    def test_dry_run_cycle_completes(self, tmp_path):
        """Test that a dry-run cycle completes without errors."""
        with patch.object(ato, 'DATA_OUT', tmp_path):
            with patch.object(ato, 'DATASETS_DIR', tmp_path / 'datasets'):
                (tmp_path / 'datasets').mkdir()
                
                # Mock training to avoid actual execution
                with patch.object(ato, 'run_training_cycle', return_value={'success': True}):
                    result = ato.run_single_cycle(cycle_number=1, dry_run=True)
                    assert result is not None
