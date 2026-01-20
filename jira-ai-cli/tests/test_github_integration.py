import pytest
import os
import requests
from unittest.mock import patch, MagicMock
from jira_ai_cli.github_integration import GitHubIntegration

# Fixture to mock environment variables for GitHub
@pytest.fixture
def mock_github_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "mock_token")
    monkeypatch.setenv("GITHUB_OWNER", "mock_owner")
    monkeypatch.setenv("GITHUB_REPO", "mock_repo")

# Fixture for a mock successful GitHub API response
@pytest.fixture
def mock_response_200():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    return mock_resp

# Test for initialization
def test_github_integration_init_success(mock_github_env):
    integrator = GitHubIntegration()
    assert integrator.github_token == "mock_token"
    assert "Authorization" in integrator.headers
    assert integrator.owner == "mock_owner"
    assert integrator.repo == "mock_repo"

def test_github_integration_init_no_token(monkeypatch, capsys):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    integrator = GitHubIntegration()
    assert integrator.github_token is None
    assert "Error: GITHUB_TOKEN environment variable not set." in capsys.readouterr().err

# Test for _make_request method
@patch('requests.request')
def test_make_request_success(mock_requests_request, mock_github_env, mock_response_200):
    mock_response_200.json.return_value = {"key": "value"}
    mock_requests_request.return_value = mock_response_200
    integrator = GitHubIntegration()
    result = integrator._make_request("GET", "test_path")
    assert result == {"key": "value"}
    mock_requests_request.assert_called_once()

@patch('requests.request')
def test_make_request_http_error(mock_requests_request, mock_github_env, mock_response_200, capsys):
    mock_response_200.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
    mock_requests_request.return_value = mock_response_200
    integrator = GitHubIntegration()
    result = integrator._make_request("GET", "test_path")
    assert result is None
    assert "GitHub API Error: 404 Client Error" in capsys.readouterr().err

@patch('requests.request')
def test_make_request_connection_error(mock_requests_request, mock_github_env, capsys):
    mock_requests_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
    integrator = GitHubIntegration()
    result = integrator._make_request("GET", "test_path")
    assert result is None
    assert "GitHub API Error: Connection failed" in capsys.readouterr().err

# Test for get_pull_request_context
@patch('jira_ai_cli.github_integration.GitHubIntegration._make_request')
def test_get_pull_request_context_success(mock_make_request, mock_github_env):
    mock_make_request.side_effect = [
        # Response for pulls/{pr_number}
        {"title": "PR Title", "body": "PR Body", "head": {"ref": "feature-branch"}},
        # Response for pulls/{pr_number}/commits
        [{"commit": {"message": "Commit 1 message"}}, {"commit": {"message": "Commit 2 message"}}]
    ]
    integrator = GitHubIntegration()
    context = integrator.get_pull_request_context(123)
    assert context["pr_number"] == 123
    assert context["title"] == "PR Title"
    assert context["description"] == "PR Body"
    assert "Commit 1 message" in context["commit_messages"]

@patch('jira_ai_cli.github_integration.GitHubIntegration._make_request')
def test_get_pull_request_context_no_pr_data(mock_make_request, mock_github_env):
    mock_make_request.return_value = None
    integrator = GitHubIntegration()
    context = integrator.get_pull_request_context(123)
    assert context is None

# Test for get_commit_context
@patch('jira_ai_cli.github_integration.GitHubIntegration._make_request')
def test_get_commit_context_success(mock_make_request, mock_github_env):
    mock_make_request.return_value = {"commit": {"message": "Single Commit Message"}}
    integrator = GitHubIntegration()
    context = integrator.get_commit_context("sha123")
    assert context["commit_sha"] == "sha123"
    assert context["message"] == "Single Commit Message"

@patch('jira_ai_cli.github_integration.GitHubIntegration._make_request')
def test_get_commit_context_no_commit_data(mock_make_request, mock_github_env):
    mock_make_request.return_value = None
    integrator = GitHubIntegration()
    context = integrator.get_commit_context("sha123")
    assert context is None

# Test for get_branch_context
@patch('jira_ai_cli.github_integration.GitHubIntegration._make_request')
def test_get_branch_context_success(mock_make_request, mock_github_env):
    # Mock response for branches/{branch_name}
    mock_make_request.side_effect = [
        {"commit": {"sha": "branch_sha"}},
        # Mock response for commits/{latest_commit_sha}
        {"commit": {"message": "Latest branch commit"}}
    ]
    integrator = GitHubIntegration()
    context = integrator.get_branch_context("main")
    assert context["branch_name"] == "main"
    assert context["latest_commit_sha"] == "branch_sha"
    assert context["latest_commit_message"] == "Latest branch commit"

@patch('jira_ai_cli.github_integration.GitHubIntegration._make_request')
def test_get_branch_context_no_branch_data(mock_make_request, mock_github_env):
    mock_make_request.return_value = None
    integrator = GitHubIntegration()
    context = integrator.get_branch_context("main")
    assert context is None