import pytest
import json
import subprocess # Added import
from unittest.mock import MagicMock, patch
from jira_ai_cli.llm_integration import LLMIntegration

# Fixture for a mock successful Gemini CLI JSON output
@pytest.fixture
def mock_gemini_success_output():
    return {
        "actions": [
            {
                "type": "create_ticket",
                "issue_type": "Bug",
                "summary": "LLM suggested summary",
                "description": "LLM suggested description",
                "labels": ["llm-generated"],
                "confidence": 0.95
            }
        ]
    }

# Test for call_gemini method
@patch('subprocess.run')
def test_call_gemini_success(mock_subprocess_run, mock_gemini_success_output):
    mock_process = MagicMock()
    mock_process.stdout = json.dumps(mock_gemini_success_output)
    mock_process.stderr = ""
    mock_process.returncode = 0
    mock_subprocess_run.return_value = mock_process

    integrator = LLMIntegration()
    prompt = "Some prompt"
    result = integrator.call_gemini(prompt)

    mock_subprocess_run.assert_called_once()
    assert result == mock_gemini_success_output

@patch('subprocess.run')
def test_call_gemini_with_markdown_json(mock_subprocess_run, mock_gemini_success_output):
    mock_process = MagicMock()
    mock_process.stdout = f"```json\n{json.dumps(mock_gemini_success_output)}\n```"
    mock_process.stderr = ""
    mock_process.returncode = 0
    mock_subprocess_run.return_value = mock_process

    integrator = LLMIntegration()
    prompt = "Some prompt"
    result = integrator.call_gemini(prompt)

    mock_subprocess_run.assert_called_once()
    assert result == mock_gemini_success_output

@patch('subprocess.run')
def test_call_gemini_file_not_found(mock_subprocess_run, capsys):
    mock_subprocess_run.side_effect = FileNotFoundError("gemini command not found")
    integrator = LLMIntegration()
    prompt = "Some prompt"
    result = integrator.call_gemini(prompt)

    assert result == {"actions": []}
    assert "Error: `gemini` command not found." in capsys.readouterr().err

@patch('subprocess.run')
def test_call_gemini_called_process_error(mock_subprocess_run, capsys):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "gemini pro", stderr="Error from Gemini")
    integrator = LLMIntegration()
    prompt = "Some prompt"
    result = integrator.call_gemini(prompt)

    out, err = capsys.readouterr()
    assert result == {"actions": []}
    assert "Error calling Gemini CLI:" in err
    assert "Error from Gemini" in err

@patch('subprocess.run')
def test_call_gemini_json_decode_error(mock_subprocess_run, capsys):
    mock_process = MagicMock()
    mock_process.stdout = "invalid json"
    mock_process.stderr = ""
    mock_process.returncode = 0
    mock_subprocess_run.return_value = mock_process

    integrator = LLMIntegration()
    prompt = "Some prompt"
    result = integrator.call_gemini(prompt)

    assert result == {"actions": []}
    assert "Error decoding JSON from Gemini CLI output:" in capsys.readouterr().err

def test_validate_gemini_output_success():
    integrator = LLMIntegration()
    valid_output = {
        "actions": [
            {"type": "create_ticket", "issue_type": "Bug", "summary": "Test", "description": "Desc", "confidence": 0.9}
        ]
    }
    # Should not raise an exception
    integrator._validate_gemini_output(valid_output)

def test_validate_gemini_output_missing_actions():
    integrator = LLMIntegration()
    invalid_output = {"no_actions_key": []}
    with pytest.raises(ValueError, match="Gemini output must be a dictionary with an 'actions' key."):
        integrator._validate_gemini_output(invalid_output)

def test_validate_gemini_output_actions_not_list():
    integrator = LLMIntegration()
    invalid_output = {"actions": "not a list"}
    with pytest.raises(ValueError, match="The 'actions' key in Gemini output must be a list."):
        integrator._validate_gemini_output(invalid_output)

def test_validate_gemini_output_action_not_dict():
    integrator = LLMIntegration()
    invalid_output = {"actions": ["not a dict"]}
    with pytest.raises(ValueError, match="Each action in Gemini output must be a dictionary with a 'type' key."):
        integrator._validate_gemini_output(invalid_output)

def test_validate_gemini_output_action_missing_type():
    integrator = LLMIntegration()
    invalid_output = {"actions": [{"no_type_key": "value"}]}
    with pytest.raises(ValueError, match="Each action in Gemini output must be a dictionary with a 'type' key."):
        integrator._validate_gemini_output(invalid_output)
