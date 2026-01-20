import pytest
import os
from unittest.mock import MagicMock, patch
from jira_ai_cli.jira_integration import JiraIntegration
from jira import JIRA, JIRAError

# Fixture to mock environment variables for Jira
@pytest.fixture
def mock_jira_env(monkeypatch):
    monkeypatch.setenv("JIRA_SERVER", "https://mock-jira.com")
    monkeypatch.setenv("JIRA_USERNAME", "mock_user")
    monkeypatch.setenv("JIRA_API_TOKEN", "mock_token")

# Test for initialization
@patch('jira_ai_cli.jira_integration.JIRA')
def test_jira_integration_init_success(mock_jira_class, mock_jira_env, capsys):
    integrator = JiraIntegration()
    mock_jira_class.assert_called_once_with(server="https://mock-jira.com", basic_auth=("mock_user", "mock_token"))
    assert integrator.jira is not None
    assert "Successfully connected to Jira." in capsys.readouterr().out

@patch('jira_ai_cli.jira_integration.JIRA')
def test_jira_integration_init_failure(mock_jira_class, mock_jira_env, capsys):
    mock_jira_class.side_effect = JIRAError("Connection Failed")
    integrator = JiraIntegration()
    assert integrator.jira is None
    assert "Error connecting to Jira:" in capsys.readouterr().err

def test_jira_integration_init_no_env_vars(monkeypatch, capsys):
    monkeypatch.delenv("JIRA_SERVER", raising=False)
    monkeypatch.delenv("JIRA_USERNAME", raising=False)
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)
    integrator = JiraIntegration()
    assert integrator.jira is None
    assert "Error: JIRA_SERVER, JIRA_USERNAME, or JIRA_API_TOKEN environment variables not set." in capsys.readouterr().err

# Test for search_issues
@patch('jira_ai_cli.jira_integration.JIRA')
def test_search_issues_success(mock_jira_class, mock_jira_env):
    mock_jira_instance = mock_jira_class.return_value
    mock_issue = MagicMock()
    mock_issue.key = "PROJ-1"
    mock_issue.fields.summary = "Test Issue"
    mock_jira_instance.search_issues.return_value = [mock_issue]

    integrator = JiraIntegration()
    issues = integrator.search_issues("project = PROJ")
    assert len(issues) == 1
    assert issues[0].key == "PROJ-1"
    mock_jira_instance.search_issues.assert_called_once_with("project = PROJ", maxResults=5)

@patch('jira_ai_cli.jira_integration.JIRA')
def test_search_issues_no_jira_connection(mock_jira_class, monkeypatch, capsys):
    monkeypatch.delenv("JIRA_SERVER", raising=False)
    integrator = JiraIntegration() # Will fail to connect
    issues = integrator.search_issues("project = PROJ")
    assert issues is None
    assert "Error: JIRA_SERVER, JIRA_USERNAME, or JIRA_API_TOKEN environment variables not set." in capsys.readouterr().err


@patch('jira_ai_cli.jira_integration.JIRA')
def test_search_issues_error(mock_jira_class, mock_jira_env, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.search_issues.side_effect = JIRAError("Search failed")
    integrator = JiraIntegration()
    issues = integrator.search_issues("project = PROJ")
    assert issues is None
    assert "Error searching Jira issues: Search failed" in capsys.readouterr().err

# Test for create_issue
@patch('jira_ai_cli.jira_integration.JIRA')
def test_create_issue_success(mock_jira_class, mock_jira_env):
    mock_jira_instance = mock_jira_class.return_value
    mock_new_issue = MagicMock()
    mock_new_issue.key = "PROJ-2"
    mock_jira_instance.create_issue.return_value = mock_new_issue

    integrator = JiraIntegration()
    issue = integrator.create_issue("PROJ", "New Summary", "New Description", "Bug", ["label1"])
    assert issue.key == "PROJ-2"
    mock_jira_instance.create_issue.assert_called_once()
    args, kwargs = mock_jira_instance.create_issue.call_args
    assert kwargs['fields']['project']['key'] == "PROJ"
    assert kwargs['fields']['summary'] == "New Summary"
    assert kwargs['fields']['labels'] == ["label1"]

@patch('jira_ai_cli.jira_integration.JIRA')
def test_create_issue_error(mock_jira_class, mock_jira_env, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.create_issue.side_effect = JIRAError("Create failed")
    integrator = JiraIntegration()
    issue = integrator.create_issue("PROJ", "New Summary", "New Description")
    assert issue is None
    assert "Error creating Jira issue: Create failed" in capsys.readouterr().err

# Test for transition_issue
@patch('jira_ai_cli.jira_integration.JIRA')
def test_transition_issue_success(mock_jira_class, mock_jira_env):
    mock_jira_instance = mock_jira_class.return_value
    mock_issue = MagicMock()
    mock_jira_instance.issue.return_value = mock_issue
    mock_jira_instance.transitions.return_value = [{"id": "1", "name": "To Do"}, {"id": "2", "name": "In Progress"}]

    integrator = JiraIntegration()
    result = integrator.transition_issue("PROJ-1", "In Progress")
    assert result is True
    mock_jira_instance.transition_issue.assert_called_once_with(mock_issue, "2")

@patch('jira_ai_cli.jira_integration.JIRA')
def test_transition_issue_not_found(mock_jira_class, mock_jira_env, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_issue = MagicMock()
    mock_jira_instance.issue.return_value = mock_issue
    mock_jira_instance.transitions.return_value = [{"id": "1", "name": "To Do"}]

    integrator = JiraIntegration()
    result = integrator.transition_issue("PROJ-1", "In Progress")
    assert result is False
    assert "Error: Transition 'In Progress' not found for issue PROJ-1." in capsys.readouterr().err

@patch('jira_ai_cli.jira_integration.JIRA')
def test_transition_issue_error(mock_jira_class, mock_jira_env, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.issue.side_effect = JIRAError("Issue not found")
    integrator = JiraIntegration()
    result = integrator.transition_issue("PROJ-1", "In Progress")
    assert result is False
    assert "Error transitioning Jira issue PROJ-1: Issue not found" in capsys.readouterr().err

# Test for add_comment
@patch('jira_ai_cli.jira_integration.JIRA')
def test_add_comment_success(mock_jira_class, mock_jira_env):
    mock_jira_instance = mock_jira_class.return_value
    mock_comment = MagicMock()
    mock_jira_instance.add_comment.return_value = mock_comment

    integrator = JiraIntegration()
    comment = integrator.add_comment("PROJ-1", "Test comment")
    assert comment is not None
    mock_jira_instance.add_comment.assert_called_once_with("PROJ-1", "Test comment")

@patch('jira_ai_cli.jira_integration.JIRA')
def test_add_comment_error(mock_jira_class, mock_jira_env, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.add_comment.side_effect = JIRAError("Comment failed")
    integrator = JiraIntegration()
    comment = integrator.add_comment("PROJ-1", "Test comment")
    assert comment is None
    assert "Error adding comment to Jira issue PROJ-1: Comment failed" in capsys.readouterr().err
