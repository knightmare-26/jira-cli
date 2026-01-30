import pytest
from unittest.mock import MagicMock, patch
from jira_ai_cli.jira_integration import JiraIntegration
from jira_ai_cli.config_manager import ConfigManager # Import ConfigManager
from jira import JIRA, JIRAError

# Fixture to mock ConfigManager.load_config()
@pytest.fixture
def mock_config_manager_load_config(monkeypatch):
    def mock_load_config(self):
        return {
            "JIRA_SERVER": "https://mock-jira.com",
            "JIRA_USERNAME": "mock_user",
            "JIRA_API_TOKEN": "mock_token"
        }
    monkeypatch.setattr(ConfigManager, "load_config", mock_load_config)

# Test for initialization
@patch('jira_ai_cli.jira_integration.JIRA')
def test_jira_integration_init_success(mock_jira_class, mock_config_manager_load_config, capsys):
    integrator = JiraIntegration()
    mock_jira_class.assert_called_once_with(server="https://mock-jira.com", basic_auth=("mock_user", "mock_token"))
    assert integrator.jira is not None
    assert "Successfully connected to Jira." in capsys.readouterr().out

@patch('jira_ai_cli.jira_integration.JIRA')
def test_jira_integration_init_failure(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_class.side_effect = JIRAError("Connection Failed")
    integrator = JiraIntegration()
    assert integrator.jira is None
    assert "Error connecting to Jira:" in capsys.readouterr().err

@patch('jira_ai_cli.jira_integration.JIRA')
def test_jira_integration_init_no_config(mock_jira_class, monkeypatch, capsys):
    def mock_load_empty_config(self):
        return {}
    monkeypatch.setattr(ConfigManager, "load_config", mock_load_empty_config)
    
    integrator = JiraIntegration()
    assert integrator.jira is None
    assert "Error: Jira configuration not found. Please run 'jira-ai config' to set up your credentials." in capsys.readouterr().err

# Test for search_issues
@patch('jira_ai_cli.jira_integration.JIRA')
def test_search_issues_success(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_issue = MagicMock()
    mock_issue.key = "PROJ-1"
    mock_issue.fields.summary = "Test Issue"
    mock_jira_instance.search_issues.return_value = [mock_issue]

    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr() 
    issues = integrator.search_issues("project = PROJ")
    assert len(issues) == 1
    assert issues[0].key == "PROJ-1"
    mock_jira_instance.search_issues.assert_called_once_with("project = PROJ", maxResults=5)

@patch('jira_ai_cli.jira_integration.JIRA')
def test_search_issues_no_config(mock_jira_class, monkeypatch, capsys):
    def mock_load_empty_config(self):
        return {}
    monkeypatch.setattr(ConfigManager, "load_config", mock_load_empty_config)

    integrator = JiraIntegration() # Will fail to connect
    issues = integrator.search_issues("project = PROJ")
    assert issues is None
    assert "Error: Jira configuration not found. Please run 'jira-ai config' to set up your credentials." in capsys.readouterr().err


@patch('jira_ai_cli.jira_integration.JIRA')
def test_search_issues_error(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.search_issues.side_effect = JIRAError("Search failed")
    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    issues = integrator.search_issues("project = PROJ")
    assert issues is None
    assert "Error searching Jira issues:" in capsys.readouterr().err

# Test for create_issue
@patch('jira_ai_cli.jira_integration.JIRA')
def test_create_issue_success(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_new_issue = MagicMock()
    mock_new_issue.key = "PROJ-2"
    mock_jira_instance.create_issue.return_value = mock_new_issue

    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    issue = integrator.create_issue("PROJ", "New Summary", "New Description", "Bug", ["label1"])
    assert issue.key == "PROJ-2"
    mock_jira_instance.create_issue.assert_called_once()
    args, kwargs = mock_jira_instance.create_issue.call_args
    assert kwargs['fields']['project']['key'] == "PROJ"
    assert kwargs['fields']['summary'] == "New Summary"
    assert kwargs['fields']['labels'] == ["label1"]

@patch('jira_ai_cli.jira_integration.JIRA')
def test_create_issue_error(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.create_issue.side_effect = JIRAError("Create failed")
    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    issue = integrator.create_issue("PROJ", "New Summary", "New Description")
    assert issue is None
    assert "Error creating Jira issue:" in capsys.readouterr().err

# Test for transition_issue
@patch('jira_ai_cli.jira_integration.JIRA')
def test_transition_issue_success(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_issue = MagicMock()
    mock_jira_instance.issue.return_value = mock_issue
    mock_jira_instance.transitions.return_value = [{"id": "1", "name": "To Do"}, {"id": "2", "name": "In Progress"}]

    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    result = integrator.transition_issue("PROJ-1", "In Progress")
    assert result is True
    mock_jira_instance.transition_issue.assert_called_once_with(mock_issue, "2")

@patch('jira_ai_cli.jira_integration.JIRA')
def test_transition_issue_not_found(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_issue = MagicMock()
    mock_jira_instance.issue.return_value = mock_issue
    mock_jira_instance.transitions.return_value = [{"id": "1", "name": "To Do"}]

    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    result = integrator.transition_issue("PROJ-1", "In Progress")
    assert result is False
    assert "Error: Transition 'In Progress' not found for issue PROJ-1." in capsys.readouterr().err

@patch('jira_ai_cli.jira_integration.JIRA')
def test_transition_issue_error(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.issue.side_effect = JIRAError("Issue not found")
    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    result = integrator.transition_issue("PROJ-1", "In Progress")
    assert result is False
    assert "Error transitioning Jira issue" in capsys.readouterr().err

# Test for add_comment
@patch('jira_ai_cli.jira_integration.JIRA')
def test_add_comment_success(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_comment = MagicMock()
    mock_jira_instance.add_comment.return_value = mock_comment

    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    comment = integrator.add_comment("PROJ-1", "Test comment")
    assert comment is not None
    mock_jira_instance.add_comment.assert_called_once_with("PROJ-1", "Test comment")

@patch('jira_ai_cli.jira_integration.JIRA')
def test_add_comment_error(mock_jira_class, mock_config_manager_load_config, capsys):
    mock_jira_instance = mock_jira_class.return_value
    mock_jira_instance.add_comment.side_effect = JIRAError("Comment failed")
    integrator = JiraIntegration()
    # Consume output from JiraIntegration init
    capsys.readouterr()
    comment = integrator.add_comment("PROJ-1", "Test comment")
    assert comment is None
    assert "Error adding comment to Jira issue" in capsys.readouterr().err
