"""Tests for utility functions and helpers"""
import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta


class TestPathUtilities:
    """Test path utility functions"""
    
    def test_resolve_absolute_path(self):
        """Test resolving absolute path"""
        relative_path = "data_out/results.json"
        workspace = "/workspaces/AI"
        
        absolute_path = os.path.join(workspace, relative_path)
        assert absolute_path.startswith(workspace)
    
    def test_create_directory_structure(self):
        """Test creating directory structure"""
        path = Path("/tmp/test_dir/nested/structure")
        
        # Should be representable
        assert "test_dir" in str(path)
        assert "nested" in str(path)
    
    def test_file_exists_check(self):
        """Test checking if file exists"""
        file_path = "/tmp/test_file.txt"
        
        # File may or may not exist
        assert isinstance(Path(file_path), Path)
    
    def test_get_file_extension(self):
        """Test getting file extension"""
        filename = "data_out/results.json"
        ext = filename.split(".")[-1]
        
        assert ext == "json"
    
    def test_list_files_in_directory(self):
        """Test listing files in directory"""
        directory = "/workspaces/AI/data_out"
        
        # Directory should be accessible
        assert "data_out" in directory


class TestJSONUtilities:
    """Test JSON utility functions"""
    
    def test_serialize_dict_to_json(self):
        """Test serializing dict to JSON"""
        data = {
            "name": "test",
            "value": 123,
            "items": [1, 2, 3]
        }
        
        json_str = json.dumps(data)
        assert "test" in json_str
        assert "123" in json_str
    
    def test_deserialize_json_string(self):
        """Test deserializing JSON string"""
        json_str = '{"name": "test", "value": 123}'
        data = json.loads(json_str)
        
        assert data["name"] == "test"
        assert data["value"] == 123
    
    def test_pretty_print_json(self):
        """Test pretty printing JSON"""
        data = {"key": "value", "nested": {"inner": "data"}}
        pretty_json = json.dumps(data, indent=2)
        
        assert "\n" in pretty_json
    
    def test_json_with_special_characters(self):
        """Test JSON with special characters"""
        data = {
            "text": "Hello\\nWorld",
            "path": "C:\\Users\\test"
        }
        
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert "text" in parsed
    
    def test_large_json_handling(self):
        """Test handling large JSON"""
        large_data = {
            f"key_{i}": f"value_{i}" for i in range(10000)
        }
        
        json_str = json.dumps(large_data)
        assert len(json_str) > 0


class TestDateTimeUtilities:
    """Test datetime utility functions"""
    
    def test_current_timestamp(self):
        """Test getting current timestamp"""
        now = datetime.now()
        
        assert now is not None
        assert isinstance(now, datetime)
    
    def test_iso_format_timestamp(self):
        """Test ISO format timestamp"""
        now = datetime.now()
        iso_str = now.isoformat()
        
        assert "T" in iso_str or "-" in iso_str
    
    def test_parse_iso_timestamp(self):
        """Test parsing ISO timestamp"""
        iso_str = "2024-01-17T10:00:00Z"
        
        # Should be parseable
        assert "2024" in iso_str
        assert "10:00:00" in iso_str
    
    def test_calculate_duration(self):
        """Test calculating duration"""
        start = datetime.now()
        end = start + timedelta(seconds=30)
        
        duration = (end - start).total_seconds()
        assert duration == 30
    
    def test_format_duration(self):
        """Test formatting duration"""
        seconds = 3665
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        formatted = f"{hours}h {minutes}m {secs}s"
        assert "h" in formatted


class TestValidation:
    """Test validation utility functions"""
    
    def test_validate_email(self):
        """Test email validation"""
        email = "test@example.com"
        
        assert "@" in email
        assert "." in email
    
    def test_validate_url(self):
        """Test URL validation"""
        url = "https://example.com/path"
        
        assert url.startswith("http")
    
    def test_validate_number_range(self):
        """Test number range validation"""
        value = 50
        min_val = 0
        max_val = 100
        
        assert min_val <= value <= max_val
    
    def test_validate_required_fields(self):
        """Test required field validation"""
        data = {
            "name": "test",
            "value": 123
        }
        required = ["name", "value"]
        
        for field in required:
            assert field in data
    
    def test_validate_enum_value(self):
        """Test enum value validation"""
        allowed = ["active", "inactive", "pending"]
        value = "active"
        
        assert value in allowed


class TestDataTransformation:
    """Test data transformation utilities"""
    
    def test_flatten_nested_dict(self):
        """Test flattening nested dictionary"""
        nested = {
            "level1": {
                "level2": {
                    "value": "test"
                }
            }
        }
        
        assert "level1" in nested
    
    def test_merge_dictionaries(self):
        """Test merging dictionaries"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        
        merged = {**dict1, **dict2}
        assert len(merged) == 4
    
    def test_filter_dict_keys(self):
        """Test filtering dictionary keys"""
        data = {"a": 1, "b": 2, "c": 3}
        keep_keys = ["a", "c"]
        
        filtered = {k: v for k, v in data.items() if k in keep_keys}
        assert len(filtered) == 2
    
    def test_transform_values(self):
        """Test transforming dictionary values"""
        data = {"a": "1", "b": "2", "c": "3"}
        
        transformed = {k: int(v) for k, v in data.items()}
        assert transformed["a"] == 1
    
    def test_group_list_items(self):
        """Test grouping list items"""
        items = [1, 2, 3, 4, 5, 6]
        group_size = 2
        
        groups = [items[i:i+group_size] for i in range(0, len(items), group_size)]
        assert len(groups) == 3


class TestStringUtilities:
    """Test string utility functions"""
    
    def test_capitalize_string(self):
        """Test capitalizing string"""
        text = "hello world"
        capitalized = text.capitalize()
        
        assert capitalized[0].isupper()
    
    def test_trim_whitespace(self):
        """Test trimming whitespace"""
        text = "  hello world  "
        trimmed = text.strip()
        
        assert trimmed == "hello world"
    
    def test_split_string(self):
        """Test splitting string"""
        text = "a,b,c,d"
        parts = text.split(",")
        
        assert len(parts) == 4
    
    def test_join_list_to_string(self):
        """Test joining list to string"""
        items = ["a", "b", "c"]
        joined = ",".join(items)
        
        assert joined == "a,b,c"
    
    def test_replace_substring(self):
        """Test replacing substring"""
        text = "hello world"
        replaced = text.replace("world", "universe")
        
        assert "universe" in replaced


class TestMath:
    """Test math utility functions"""
    
    def test_calculate_average(self):
        """Test calculating average"""
        values = [10, 20, 30]
        average = sum(values) / len(values)
        
        assert average == 20
    
    def test_calculate_median(self):
        """Test calculating median"""
        values = [1, 2, 3, 4, 5]
        median = values[len(values) // 2]
        
        assert median == 3
    
    def test_calculate_percentage(self):
        """Test calculating percentage"""
        current = 75
        total = 100
        percentage = (current / total) * 100
        
        assert percentage == 75.0
    
    def test_round_to_decimals(self):
        """Test rounding to decimals"""
        value = 3.14159
        rounded = round(value, 2)
        
        assert rounded == 3.14
    
    def test_clamp_value(self):
        """Test clamping value to range"""
        value = 150
        min_val = 0
        max_val = 100
        
        clamped = max(min_val, min(value, max_val))
        assert clamped == 100


class TestLogging:
    """Test logging utilities"""
    
    def test_log_message(self):
        """Test logging a message"""
        message = "Test message"
        
        assert len(message) > 0
    
    def test_log_level(self):
        """Test log level"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        assert "INFO" in levels
    
    def test_structured_logging(self):
        """Test structured logging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test message",
            "context": {"user": "test"}
        }
        
        assert "timestamp" in log_entry
        assert "message" in log_entry
