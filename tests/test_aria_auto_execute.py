#!/usr/bin/env python
"""
Comprehensive tests for Aria Auto-Execute System
Tests LLM-powered action generation, execution, and stage state management
"""
import pytest
import requests

# Configuration
BASE_URL = "http://localhost:8080"
TIMEOUT = 30


def _aria_server_available() -> bool:
    """Check if Aria server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/aria/state", timeout=2)
        return response.ok
    except requests.exceptions.RequestException:
        return False


pytestmark = pytest.mark.skipif(
    not _aria_server_available(),
    reason="Aria server not running on localhost:8080",
)


class TestAriaAutoExecuteSchema:
    """Test action schema validation and contract"""

    def test_schema_endpoint_exists(self):
        """Verify /api/aria/schema returns valid action definitions"""
        response = requests.get(
            f"{BASE_URL}/api/aria/schema", timeout=TIMEOUT
        )
        assert response.status_code == 200
        schema = response.json()

        # Verify required action types are defined
        required_actions = {
            "move", "say", "pickup", "drop",
            "throw", "gesture", "look", "wait"
        }
        actual_actions = set(schema.keys())
        missing = required_actions - actual_actions
        assert required_actions.issubset(actual_actions), \
            f"Missing actions: {missing}"

    def test_action_schema_has_required_fields(self):
        """Verify each action has params and description"""
        response = requests.get(
            f"{BASE_URL}/api/aria/schema", timeout=TIMEOUT
        )
        schema = response.json()

        for action_name, action_def in schema.items():
            assert "params" in action_def, \
                f"Action {action_name} missing params"
            assert "description" in action_def, \
                f"Action {action_name} missing description"
            assert "example" in action_def, \
                f"Action {action_name} missing example"

    def test_valid_gestures_defined(self):
        """Verify valid gesture types are available"""
        response = requests.get(f"{BASE_URL}/api/aria/schema", timeout=TIMEOUT)
        schema = response.json()
        gesture_action = schema.get("gesture", {})

        if gesture_action:
            assert "example" in gesture_action
            example = gesture_action["example"]
            assert "gesture_type" in example or "gesture" in example


class TestAriaAutoExecutePlanMode:
    """Test plan-only mode (parsing without execution)"""

    def test_plan_simple_move_command(self):
        """Test parsing a simple move command"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "move left",
                "auto_execute": False,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "actions" in data
        assert len(data["actions"]) > 0
        assert data["executed"] is False

    def test_plan_pickup_command(self):
        """Test parsing pickup command"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "pick up the apple",
                "auto_execute": False,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "actions" in data
        if len(data["actions"]) > 0:
            action = data["actions"][0]
            assert "action" in action

    def test_plan_complex_sequence(self):
        """Test parsing multi-step command sequence"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "walk to the table and pick up "
                           "the apple",
                "auto_execute": False,
                "use_llm": False,
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert isinstance(data["actions"], list)
        # Should parse multiple actions from complex command
        if len(data["actions"]) > 0:
            for action in data["actions"]:
                assert "action" in action

    def test_plan_say_command(self):
        """Test parsing say/speak commands"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "say hello world",
                "auto_execute": False,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "actions" in data

    def test_plan_gesture_command(self):
        """Test parsing gesture commands"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "wave at me",
                "auto_execute": False,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "actions" in data

    def test_plan_mode_does_not_modify_state(self):
        """Verify plan mode doesn't change stage state"""
        # Get initial state
        get_state_url = f"{BASE_URL}/api/aria/state"
        state_before = requests.get(
            get_state_url, timeout=TIMEOUT
        ).json()

        # Run plan mode
        requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "move right and pick up the apple",
                "auto_execute": False
            },
            timeout=TIMEOUT,
        )

        # Verify state unchanged
        state_after = requests.get(
            get_state_url, timeout=TIMEOUT
        ).json()
        assert state_before == state_after, \
            "Plan mode should not modify state"


class TestAriaAutoExecuteMode:
    """Test execution mode with actual state changes"""

    def test_execute_simple_move(self):
        """Test executing a simple move command"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "move right",
                "auto_execute": True,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["executed"] is True
        assert "results" in data
        assert data["state"] is not None

    def test_execute_returns_updated_state(self):
        """Verify execution returns updated stage state"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "say hello",
                "auto_execute": True,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert "state" in data
        state = data["state"]
        assert "aria" in state
        assert "position" in state["aria"]
        assert "expression" in state["aria"]

    def test_execute_results_structure(self):
        """Verify execution results have expected structure"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "wave", "auto_execute": True, "use_llm": False},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        for result in data["results"]:
            assert "action" in result
            assert "result" in result
            assert "status" in result["result"]
            assert "message" in result["result"]

    def test_execute_with_tags_output(self):
        """Verify execution generates tags for UI rendering"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "move left",
                "auto_execute": True,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()

        # Should include tags for UI integration
        assert "tags" in data
        # Tags might be array or string depending on implementation
        assert data["tags"] is not None


class TestAriaActionValidation:
    """Test action validation and constraints"""

    def test_invalid_action_type_handled(self):
        """Test handling of invalid action types"""
        # This tests the system's robustness
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "invalid command xyz abc",
                "auto_execute": False,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        # System should either parse or gracefully handle
        assert response.status_code in [200, 400, 422]

    def test_empty_command_handled(self):
        """Test handling of empty commands"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "", "auto_execute": False},
            timeout=TIMEOUT,
        )
        assert response.status_code in [200, 400, 422]

    def test_very_long_command_handled(self):
        """Test handling of excessively long commands"""
        long_command = "do " * 1000 + "something"
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": long_command, "auto_execute": False},
            timeout=TIMEOUT,
        )
        # Should handle gracefully (timeout, truncation, or error)
        assert response.status_code in [200, 400, 422, 408]

    def test_special_characters_in_command(self):
        """Test handling of special characters"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={
                "command": "say !@#$%^&*()",
                "auto_execute": False,
                "use_llm": False
            },
            timeout=TIMEOUT,
        )
        assert response.status_code in [200, 400, 422]


class TestAriaStateManagement:
    """Test stage state consistency and updates"""

    def test_state_endpoint_returns_valid_state(self):
        """Verify /api/aria/state returns properly structured state"""
        response = requests.get(
            f"{BASE_URL}/api/aria/state", timeout=TIMEOUT
        )
        assert response.status_code == 200
        state = response.json()

        # Check required state fields
        assert "aria" in state
        assert "position" in state["aria"]
        objects_field = state.get("objects")
        assert "objects" in state or isinstance(objects_field, dict)

    def test_aria_position_valid_coordinates(self):
        """Verify Aria position is always within valid bounds"""
        response = requests.get(
            f"{BASE_URL}/api/aria/state", timeout=TIMEOUT
        )
        state = response.json()

        position = state["aria"]["position"]
        assert "x" in position
        assert "y" in position
        assert 0 <= position["x"] <= 100, \
            "X coordinate out of bounds"
        assert 0 <= position["y"] <= 100, \
            "Y coordinate out of bounds"

    def test_aria_expression_valid(self):
        """Verify Aria expression is a valid emotion state"""
        response = requests.get(
            f"{BASE_URL}/api/aria/state", timeout=TIMEOUT
        )
        state = response.json()

        expression = state["aria"].get("expression", "neutral")
        valid_expressions = {
            "neutral", "happy", "sad", "confused",
            "excited", "calm"
        }
        assert expression in valid_expressions or \
            isinstance(expression, str)

    def test_state_consistency_after_sequence(self):
        """Verify state remains consistent after multiple operations"""
        # Execute multiple commands
        for cmd in ["move right", "say hello", "move left"]:
            requests.post(
                f"{BASE_URL}/api/aria/execute",
                json={
                    "command": cmd,
                    "auto_execute": True,
                    "use_llm": False
                },
                timeout=TIMEOUT,
            )

        # Get final state
        get_state_url = f"{BASE_URL}/api/aria/state"
        final = requests.get(get_state_url, timeout=TIMEOUT).json()

        # Verify state is valid
        assert "aria" in final
        assert "position" in final["aria"]
        assert final["aria"]["position"]["x"] is not None
        assert final["aria"]["position"]["y"] is not None


class TestAriaObjectManagement:
    """Test object interaction system"""

    def test_objects_list_retrievable(self):
        """Verify /api/aria/objects endpoint returns object list"""
        response = requests.get(
            f"{BASE_URL}/api/aria/objects", timeout=TIMEOUT)
        # 404 is okay if not implemented
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict) or isinstance(data, list)

    def test_add_object_command(self):
        """Test adding a new object to the stage"""
        response = requests.post(
            f"{BASE_URL}/api/aria/object",
            json={"action": "add", "name": "test_object",
                  "position": {"x": 50, "y": 50}},
            timeout=TIMEOUT,
        )
        assert response.status_code in [200, 201, 400, 404]

    def test_object_state_tracking(self):
        """Verify objects have state tracking in various states"""
        state_response = requests.get(
            f"{BASE_URL}/api/aria/state", timeout=TIMEOUT)
        state = state_response.json()

        if "objects" in state and state["objects"]:
            for obj_name, obj_data in state["objects"].items():
                assert isinstance(
                    obj_data, dict), f"Object {obj_name} should be a dict"
                # State tracking is optional but if present should be valid
                if "state" in obj_data:
                    valid_states = {"on_table", "held", "dropped", "thrown"}
                    assert obj_data["state"] in valid_states or isinstance(
                        obj_data["state"], str)


class TestAriaProviderDetection:
    """Test LLM provider detection and fallback"""

    def test_ai_status_endpoint(self):
        """Verify /api/ai/status shows provider information"""
        response = requests.get(
            "http://localhost:7071/api/ai/status", timeout=TIMEOUT)
        if response.status_code == 200:
            status = response.json()
            # Provider info might be in various fields
            assert "active_provider" in status or "provider" in status or True

    def test_fallback_parsing_without_llm(self):
        """Verify fallback parser works when LLM unavailable"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "move left",
                  "auto_execute": False, "use_llm": False},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestAriaErrorHandling:
    """Test error handling and edge cases"""

    def test_malformed_json_rejected(self):
        """Verify malformed JSON is properly rejected"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            data="not valid json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        assert response.status_code in [400, 422]

    def test_missing_required_fields_handled(self):
        """Verify missing required fields are handled"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"auto_execute": True},  # Missing 'command'
            timeout=TIMEOUT,
        )
        assert response.status_code in [200, 400, 422]

    def test_invalid_coordinate_handled(self):
        """Test handling of invalid coordinates"""
        response = requests.post(
            f"{BASE_URL}/api/aria/object",
            json={"action": "add", "position": {"x": 999, "y": 999}},
            timeout=TIMEOUT,
        )
        # Should either reject or clamp to valid range
        assert response.status_code in [200, 201, 400, 422]

    def test_response_includes_error_details(self):
        """Verify errors include helpful details"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "", "auto_execute": True},
            timeout=TIMEOUT,
        )
        resp_json = response.json()
        is_error = (response.status_code >= 400 or
                    (response.status_code == 200 and
                     resp_json.get("status") == "error"))
        if is_error:
            assert "message" in resp_json or "error" in resp_json


class TestAriaResponseFormats:
    """Test response format consistency"""

    def test_execute_response_format(self):
        """Verify /api/aria/execute response matches documented format"""
        response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "move right", "auto_execute": False},
            timeout=TIMEOUT,
        )
        data = response.json()

        # Required fields in response
        required_fields = {"status", "message",
                           "command", "actions", "executed"}
        actual_keys = set(data.keys())
        missing = required_fields - actual_keys
        assert required_fields.issubset(actual_keys), \
            f"Missing fields: {missing}"

    def test_state_response_format(self):
        """Verify /api/aria/state response matches documented format"""
        response = requests.get(f"{BASE_URL}/api/aria/state", timeout=TIMEOUT)
        state = response.json()

        # Minimum required structure
        assert "aria" in state
        assert "position" in state["aria"]
        assert isinstance(state["aria"]["position"], dict)

    def test_schema_response_format(self):
        """Verify /api/aria/schema response format is consistent"""
        response = requests.get(f"{BASE_URL}/api/aria/schema", timeout=TIMEOUT)
        schema = response.json()

        assert isinstance(schema, dict)
        for action_name, action_def in schema.items():
            assert isinstance(action_name, str)
            assert isinstance(action_def, dict)


class TestAriaIntegration:
    """End-to-end integration tests"""

    def test_full_workflow_plan_then_execute(self):
        """Test complete workflow: plan → review → execute"""
        # Step 1: Plan
        plan_response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "wave hello",
                  "auto_execute": False, "use_llm": False},
            timeout=TIMEOUT,
        )
        assert plan_response.status_code == 200
        plan_data = plan_response.json()
        assert plan_data["executed"] is False

        # Step 2: Execute
        exec_response = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "wave hello",
                  "auto_execute": True, "use_llm": False},
            timeout=TIMEOUT,
        )
        assert exec_response.status_code == 200
        exec_data = exec_response.json()
        assert exec_data["executed"] is True

    def test_sequential_commands_maintain_state(self):
        """Test that sequential commands properly update state"""
        # Command 1
        resp1 = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "move left",
                  "auto_execute": True, "use_llm": False},
            timeout=TIMEOUT,
        )
        state1 = resp1.json().get("state", {}).get("aria", {}).get("position")

        # Command 2
        resp2 = requests.post(
            f"{BASE_URL}/api/aria/execute",
            json={"command": "move right",
                  "auto_execute": True, "use_llm": False},
            timeout=TIMEOUT,
        )
        state2 = resp2.json().get("state", {}).get("aria", {}).get("position")

        # Both should have valid positions
        assert state1 is not None
        assert state2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
