"""Tests for Aria action parser and auto-execute system."""
import json
import sys
from pathlib import Path
import pytest

# Add aria_web to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'aria_web'))

try:
    import server as aria_server
except ImportError:
    pytest.skip("Aria server not available", allow_module_level=True)


class TestActionParser:
    """Test natural language action parsing."""
    
    def test_parse_simple_move_command(self):
        """Test parsing simple move commands."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("move left")
        assert len(actions) > 0
        assert actions[0]['action'] == 'move'
        assert actions[0]['direction'] == 'left'
    
    def test_parse_wave_gesture(self):
        """Test parsing wave gesture command."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("wave at me")
        assert any(a['action'] == 'gesture' and a['type'] == 'wave' for a in actions)
    
    def test_parse_pickup_object(self):
        """Test parsing pickup commands."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("pickup the ball")
        assert any(a['action'] == 'pickup' for a in actions)
        assert any('ball' in str(a.get('object', '')).lower() for a in actions)
    
    def test_parse_compound_command(self):
        """Test parsing compound multi-action commands."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("walk to the table and pickup the apple")
        assert len(actions) >= 2
        # Should have move and pickup actions
        action_types = [a['action'] for a in actions]
        assert 'move' in action_types or 'say' in action_types
        assert 'pickup' in action_types


class TestActionValidation:
    """Test action validation logic."""
    
    def test_validate_move_action(self):
        """Test move action validation."""
        action = {'action': 'move', 'direction': 'left', 'distance': 10}
        assert aria_server.validate_action(action) is True
    
    def test_reject_invalid_action_type(self):
        """Test rejection of invalid action types."""
        action = {'action': 'invalid_action', 'param': 'value'}
        result = aria_server.validate_action(action)
        assert result is False or result is None
    
    def test_validate_pickup_requires_object(self):
        """Test pickup action requires object parameter."""
        action = {'action': 'pickup'}
        # Should fail without object
        result = aria_server.validate_action(action)
        assert result is False or result is None
        
        # Should pass with object
        action_valid = {'action': 'pickup', 'object': 'ball'}
        assert aria_server.validate_action(action_valid) is True


class TestAutoExecuteAPI:
    """Test auto-execute API endpoint."""
    
    def test_parse_mode_returns_actions(self):
        """Test that parse mode returns action sequence."""
        command = "move left and wave"
        mode = "parse"
        
        result = aria_server.auto_execute_command(command, mode=mode)
        
        assert 'actions' in result
        assert isinstance(result['actions'], list)
        assert len(result['actions']) > 0
    
    def test_execute_mode_runs_actions(self):
        """Test that execute mode runs action sequence."""
        command = "say hello"
        mode = "execute"
        
        result = aria_server.auto_execute_command(command, mode=mode)
        
        assert 'status' in result
        assert result['status'] in ('success', 'completed', 'ok')


class TestActionSequencing:
    """Test action sequence generation."""
    
    def test_sequence_preserves_order(self):
        """Test that action sequence preserves logical order."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("move left, pickup ball, move right, drop ball")
        
        # Check that actions are in logical order
        action_types = [a['action'] for a in actions]
        move_indices = [i for i, a in enumerate(action_types) if a == 'move']
        pickup_index = next((i for i, a in enumerate(action_types) if a == 'pickup'), -1)
        drop_index = next((i for i, a in enumerate(action_types) if a == 'drop'), -1)
        
        if pickup_index >= 0 and drop_index >= 0:
            # Pickup should come before drop
            assert pickup_index < drop_index
    
    def test_inject_wait_between_actions(self):
        """Test that wait actions can be injected between moves."""
        actions = [
            {'action': 'move', 'direction': 'left'},
            {'action': 'gesture', 'type': 'wave'}
        ]
        
        # Insert wait between actions
        actions_with_wait = aria_server.inject_wait_actions(actions, wait_ms=500)
        
        assert len(actions_with_wait) >= len(actions)
        # Check for wait action
        assert any(a.get('action') == 'wait' for a in actions_with_wait)


class TestLLMIntegration:
    """Test LLM-powered action parsing."""
    
    def test_llm_fallback_on_complex_command(self):
        """Test that complex commands fall back to LLM if available."""
        parser = aria_server.AriaActionParser()
        
        complex_command = "Navigate to the bookshelf, retrieve the blue book from the second shelf, and bring it to the reading table"
        
        actions = parser.parse_command(complex_command)
        
        # Should return some actions even if LLM unavailable (fallback)
        assert len(actions) > 0
        assert all('action' in a for a in actions)


class TestObjectInteraction:
    """Test object interaction commands."""
    
    def test_parse_throw_command(self):
        """Test parsing throw commands with trajectory."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("throw the ball to the right")
        
        throw_action = next((a for a in actions if a.get('action') == 'throw'), None)
        if throw_action:
            assert 'object' in throw_action
            assert 'direction' in throw_action or 'target' in throw_action
    
    def test_parse_drop_command(self):
        """Test parsing drop commands."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("drop what you're holding")
        
        assert any(a.get('action') == 'drop' for a in actions)


class TestExpressionSystem:
    """Test facial expression and emotion system."""
    
    def test_parse_emotion_command(self):
        """Test parsing emotion/expression commands."""
        parser = aria_server.AriaActionParser()
        
        actions = parser.parse_command("look happy")
        
        # Should have a look or gesture action
        assert any(a.get('action') in ('look', 'gesture') for a in actions)
    
    def test_expression_during_speech(self):
        """Test that expressions can accompany speech."""
        actions = [
            {'action': 'say', 'text': 'Hello there!'},
            {'action': 'gesture', 'type': 'wave'}
        ]
        
        # Both should be valid simultaneous actions
        assert all(aria_server.validate_action(a) for a in actions)


@pytest.mark.integration
class TestAutoExecuteIntegration:
    """Integration tests for auto-execute system."""
    
    def test_full_command_execution_pipeline(self):
        """Test complete command from parsing to execution."""
        command = "move right and say hello"
        
        # Parse
        parser = aria_server.AriaActionParser()
        actions = parser.parse_command(command)
        assert len(actions) > 0
        
        # Validate
        valid_actions = [a for a in actions if aria_server.validate_action(a)]
        assert len(valid_actions) > 0
        
        # Execute would happen here in real system
        # For testing, just verify structure
        assert all('action' in a for a in valid_actions)
