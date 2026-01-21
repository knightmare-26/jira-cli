import pytest
import os
import json
from unittest.mock import patch
from jira_ai_cli.config_manager import ConfigManager, CONFIG_DIR # Keep CONFIG_DIR for _ensure_config_dir test logic

# Fixture to set up a temporary config file path for each test
@pytest.fixture
def temp_config_file_path(tmp_path):
    # Create a temporary directory for the config file
    temp_dir = tmp_path / ".jira-ai-cli"
    temp_dir.mkdir()
    # Return the full path to the temporary config file
    return str(temp_dir / "config.json")

# Test for _ensure_config_dir
def test_ensure_config_dir_creates_dir(temp_config_file_path, capsys):
    # Get the directory part of the temp_config_file_path
    temp_dir = os.path.dirname(temp_config_file_path)
    if os.path.exists(temp_dir):
        os.rmdir(temp_dir) # Remove dir to test creation

    manager = ConfigManager(config_file_path=temp_config_file_path)
    assert os.path.exists(temp_dir)
    assert os.path.isdir(temp_dir)
    assert f"Created configuration directory at {temp_dir}" in capsys.readouterr().out

def test_ensure_config_dir_exists_no_error(temp_config_file_path, capsys):
    # Ensure the directory exists before initializing ConfigManager
    temp_dir = os.path.dirname(temp_config_file_path)
    os.makedirs(temp_dir, exist_ok=True)
    manager = ConfigManager(config_file_path=temp_config_file_path) # Should not raise error if dir already exists
    assert os.path.exists(temp_dir)
    assert capsys.readouterr().err == "" # No error message if dir already exists

# Test for save_config
def test_save_config_success(temp_config_file_path, capsys):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    test_data = {"key": "value", "number": 123}
    assert manager.save_config(test_data) is True
    
    with open(temp_config_file_path, 'r') as f:
        loaded_data = json.load(f)
    assert loaded_data == test_data
    assert f"Configuration saved to {temp_config_file_path}" in capsys.readouterr().out

@patch('builtins.open', side_effect=IOError("Permission denied"))
def test_save_config_io_error(mock_open, temp_config_file_path, capsys):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    test_data = {"key": "value"}
    # Consume init output if any
    capsys.readouterr()
    assert manager.save_config(test_data) is False
    assert "Error writing to configuration file" in capsys.readouterr().err

# Test for load_config
def test_load_config_success(temp_config_file_path, capsys):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    test_data = {"key": "value", "number": 123}
    with open(temp_config_file_path, 'w') as f:
        json.dump(test_data, f)
    
    # Consume init output if any
    capsys.readouterr()
    loaded_data = manager.load_config()
    assert loaded_data == test_data

def test_load_config_file_not_found(temp_config_file_path):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    # Ensure config file doesn't exist
    if os.path.exists(temp_config_file_path):
        os.remove(temp_config_file_path)
    
    loaded_data = manager.load_config()
    assert loaded_data == {}

def test_load_config_json_decode_error(temp_config_file_path, capsys):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    with open(temp_config_file_path, 'w') as f:
        f.write("invalid json")
    
    # Consume init output if any
    capsys.readouterr()
    loaded_data = manager.load_config()
    assert loaded_data == {}
    assert "Error reading or parsing configuration file" in capsys.readouterr().err

def test_load_config_io_error(temp_config_file_path, capsys):
    # Ensure the config file actually exists so that os.path.exists returns True
    # but the subsequent `open` call fails due to the patch.
    temp_dir = os.path.dirname(temp_config_file_path)
    os.makedirs(temp_dir, exist_ok=True)
    with open(temp_config_file_path, 'w') as f:
        f.write("{}") # Write some valid JSON to ensure it's a file

    manager = ConfigManager(config_file_path=temp_config_file_path)
    # Clear any output from init (like "Created configuration directory...")
    capsys.readouterr() 

    # Now call load_config which should trigger the patched open and the IOError
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        loaded_data = manager.load_config()
    out, err = capsys.readouterr() # Capture output produced by load_config
    
    assert loaded_data == {}
    assert "Error reading or parsing configuration file" in err
    assert "Permission denied" in err # Check for the specific error message text

# Test for get_value
def test_get_value_exists(temp_config_file_path, capsys):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    test_data = {"key1": "value1", "key2": "value2"}
    with open(temp_config_file_path, 'w') as f:
        json.dump(test_data, f)
    
    # Consume init output if any
    capsys.readouterr()
    assert manager.get_value("key1") == "value1"
    assert manager.get_value("key2") == "value2"

def test_get_value_not_exists(temp_config_file_path, capsys):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    test_data = {"key1": "value1"}
    with open(temp_config_file_path, 'w') as f:
        json.dump(test_data, f)
    
    # Consume init output if any
    capsys.readouterr()
    assert manager.get_value("non_existent_key") is None

def test_get_value_no_config_file(temp_config_file_path):
    manager = ConfigManager(config_file_path=temp_config_file_path)
    if os.path.exists(temp_config_file_path):
        os.remove(temp_config_file_path)
    
    assert manager.get_value("any_key") is None
