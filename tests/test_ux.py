import pytest
import os
from unittest.mock import MagicMock, patch
from jira_ai_cli.ux import AnimationManager, JIRA_CLI_BANNER

# Fixture to mock os.environ
@pytest.fixture
def mock_os_environ(monkeypatch):
    mock_env = {}
    monkeypatch.setattr(os, 'environ', mock_env)
    return mock_env

# Test for AnimationManager initialization
def test_animation_manager_enabled_by_default(mock_os_environ):
    manager = AnimationManager()
    assert manager.animation_enabled is True
    assert hasattr(manager, 'spinner')

def test_animation_manager_disabled_by_flag(mock_os_environ):
    manager = AnimationManager(no_animation=True)
    assert manager.animation_enabled is False
    assert not hasattr(manager, 'spinner')

def test_animation_manager_disabled_by_ci_env(mock_os_environ):
    mock_os_environ["CI"] = "true"
    manager = AnimationManager()
    assert manager.animation_enabled is False
    assert not hasattr(manager, 'spinner')

def test_animation_manager_flag_overrides_ci_false(mock_os_environ):
    mock_os_environ["CI"] = "false" # CI is explicitly false
    manager = AnimationManager(no_animation=True)
    assert manager.animation_enabled is False
    assert not hasattr(manager, 'spinner')

# Test for show_banner
@patch('click.echo')
@patch('click.style')
def test_show_banner_enabled(mock_style, mock_echo, mock_os_environ):
    manager = AnimationManager()
    manager.show_banner()
    assert mock_echo.call_count == 2
    mock_style.assert_any_call(JIRA_CLI_BANNER, fg='cyan')
    mock_style.assert_any_call("LLM-Assisted CLI\n", fg='blue')

@patch('click.echo')
def test_show_banner_disabled(mock_echo, mock_os_environ):
    manager = AnimationManager(no_animation=True)
    manager.show_banner()
    mock_echo.assert_not_called()

# Test for spinner methods (start, succeed, fail)
@patch('jira_ai_cli.ux.Halo')
def test_spinner_start_enabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager()
    manager.start("Loading...")
    mock_halo_class.return_value.start.assert_called_once_with("Loading...")

@patch('jira_ai_cli.ux.Halo')
def test_spinner_start_disabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager(no_animation=True)
    manager.start("Loading...")
    mock_halo_class.return_value.start.assert_not_called()

@patch('jira_ai_cli.ux.Halo')
def test_spinner_succeed_enabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager()
    manager.succeed("Success!")
    mock_halo_class.return_value.succeed.assert_called_once_with("Success!")

@patch('jira_ai_cli.ux.Halo')
def test_spinner_succeed_disabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager(no_animation=True)
    manager.succeed("Success!")
    mock_halo_class.return_value.succeed.assert_not_called()

@patch('jira_ai_cli.ux.Halo')
def test_spinner_fail_enabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager()
    manager.fail("Failed!")
    mock_halo_class.return_value.fail.assert_called_once_with("Failed!")

@patch('jira_ai_cli.ux.Halo')
def test_spinner_fail_disabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager(no_animation=True)
    manager.fail("Failed!")
    mock_halo_class.return_value.fail.assert_not_called()

@patch('jira_ai_cli.ux.Halo')
def test_spinner_stop_enabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager()
    manager.stop()
    mock_halo_class.return_value.stop.assert_called_once()

@patch('jira_ai_cli.ux.Halo')
def test_spinner_stop_disabled(mock_halo_class, mock_os_environ):
    manager = AnimationManager(no_animation=True)
    manager.stop()
    mock_halo_class.return_value.stop.assert_not_called()
