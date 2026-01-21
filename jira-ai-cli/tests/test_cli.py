import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
import json
import os

from jira_ai_cli.cli import cli
from jira_ai_cli.config_manager import ConfigManager
from jira_ai_cli.action_orchestrator import ActionOrchestrator
from jira_ai_cli.ux import AnimationManager # Import AnimationManager for patching

# Fixture for CLI runner
@pytest.fixture
def runner():
    return CliRunner()

# Fixture for a mock ConfigManager (for the 'config' command and integrators)
@pytest.fixture
def mock_config_manager(monkeypatch):
    mock_manager = MagicMock(spec=ConfigManager)
    mock_manager.load_config.return_value = {
        "JIRA_SERVER": "https://mock.jira.com",
        "JIRA_USERNAME": "mockuser",
        "JIRA_API_TOKEN": "mocktoken",
        "GITHUB_OWNER": "mockowner",
        "GITHUB_REPO": "mockrepo",
        "GITHUB_TOKEN": "mockghtoken"
    }
    # Patch ConfigManager in cli, github_integration, and jira_integration
    monkeypatch.setattr('jira_ai_cli.cli.ConfigManager', MagicMock(return_value=mock_manager))
    monkeypatch.setattr('jira_ai_cli.github_integration.ConfigManager', MagicMock(return_value=mock_manager))
    monkeypatch.setattr('jira_ai_cli.jira_integration.ConfigManager', MagicMock(return_value=mock_manager))
    return mock_manager

# Test cases for the 'config' command
def test_config_command_prompts_and_saves(runner, mock_config_manager):
    inputs = [
        "https://test.jira.com", "testuser", "testapitoken",
        "testorg", "testrepo", "testghtoken"
    ]
    result = runner.invoke(cli, ["config"], input="\n".join(inputs))

    assert result.exit_code == 0
    mock_config_manager.save_config.assert_called_once_with({
        "JIRA_SERVER": "https://test.jira.com",
        "JIRA_USERNAME": "testuser",
        "JIRA_API_TOKEN": "testapitoken",
        "GITHUB_OWNER": "testorg",
        "GITHUB_REPO": "testrepo",
        "GITHUB_TOKEN": "testghtoken",
    })

# Test cases for the 'suggest' command
@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_no_options(mock_animation_manager_class, mock_action_orchestrator_class, runner):
    result = runner.invoke(cli, ["suggest"])
    assert result.exit_code != 0 # Should exit with error
    mock_action_orchestrator_class.return_value.suggest_actions.assert_not_called()

@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_multiple_options(mock_animation_manager_class, mock_action_orchestrator_class, runner):
    result = runner.invoke(cli, ["suggest", "--pr", "123", "--branch", "feature"])
    assert result.exit_code != 0 # Should exit with error
    mock_action_orchestrator_class.return_value.suggest_actions.assert_not_called()

@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_with_pr_calls_orchestrator(mock_animation_manager_class, mock_action_orchestrator_class, runner):
    # Mock return values for orchestrator methods
    mock_action_orchestrator_class.return_value.suggest_actions.return_value = [{"type": "create_ticket"}]
    mock_action_orchestrator_class.return_value.present_and_execute_actions.return_value = None

    result = runner.invoke(cli, ["suggest", "--pr", "123"])
    assert result.exit_code == 0
    mock_action_orchestrator_class.assert_called_once() # Ensure ActionOrchestrator is instantiated
    mock_action_orchestrator_class.return_value.suggest_actions.assert_called_once_with(pr=123, commit=None, branch=None)
    mock_action_orchestrator_class.return_value.present_and_execute_actions.assert_called_once()
    mock_animation_manager_class.return_value.show_banner.assert_called_once()


@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_with_commit_calls_orchestrator(mock_animation_manager_class, mock_action_orchestrator_class, runner):
    mock_action_orchestrator_class.return_value.suggest_actions.return_value = [{"type": "create_ticket"}]
    result = runner.invoke(cli, ["suggest", "--commit", "abc123def"])
    assert result.exit_code == 0
    mock_action_orchestrator_class.return_value.suggest_actions.assert_called_once_with(pr=None, commit="abc123def", branch=None)
    mock_animation_manager_class.return_value.show_banner.assert_called_once()


@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_with_branch_calls_orchestrator(mock_animation_manager_class, mock_action_orchestrator_class, runner):
    mock_action_orchestrator_class.return_value.suggest_actions.return_value = [{"type": "create_ticket"}]
    result = runner.invoke(cli, ["suggest", "--branch", "main"])
    assert result.exit_code == 0
    mock_action_orchestrator_class.return_value.suggest_actions.assert_called_once_with(pr=None, commit=None, branch="main")
    mock_animation_manager_class.return_value.show_banner.assert_called_once()


@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_animation_enabled_by_default(mock_animation_manager_class, mock_action_orchestrator_class, runner, monkeypatch):
    monkeypatch.setenv("CI", "false") # Ensure CI is not "true"
    result = runner.invoke(cli, ["suggest", "--pr", "123"])
    assert result.exit_code == 0
    mock_animation_manager_class.assert_called_once_with(no_animation=False)
    mock_animation_manager_class.return_value.show_banner.assert_called_once()


@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_animation_disabled_by_flag(mock_animation_manager_class, mock_action_orchestrator_class, runner):
    result = runner.invoke(cli, ["suggest", "--pr", "123", "--no-animation"])
    assert result.exit_code == 0
    mock_animation_manager_class.assert_called_once_with(no_animation=True)
    mock_animation_manager_class.return_value.show_banner.assert_called_once()

@patch('jira_ai_cli.cli.ActionOrchestrator')
@patch('jira_ai_cli.cli.AnimationManager') # Patch AnimationManager for suggest tests
def test_suggest_command_animation_disabled_by_ci_env(mock_animation_manager_class, mock_action_orchestrator_class, runner, monkeypatch):
    monkeypatch.setenv("CI", "true")
    result = runner.invoke(cli, ["suggest", "--pr", "123"])
    assert result.exit_code == 0
    mock_animation_manager_class.assert_called_once_with(no_animation=False) # flag is false
    mock_animation_manager_class.return_value.show_banner.assert_called_once() # Still called, but anim_manager internally disables it

