import pytest
import json
from unittest.mock import MagicMock, patch
from jira_ai_cli.action_orchestrator import ActionOrchestrator
from jira_ai_cli.github_integration import GitHubIntegration
from jira_ai_cli.jira_integration import JiraIntegration
from jira_ai_cli.llm_integration import LLMIntegration
from jira_ai_cli.policy_engine import PolicyEngine
from jira_ai_cli.ux import AnimationManager

@pytest.fixture
def mock_integrations():
    return {
        "github": MagicMock(spec=GitHubIntegration),
        "jira": MagicMock(spec=JiraIntegration),
        "llm": MagicMock(spec=LLMIntegration),
        "policy": MagicMock(spec=PolicyEngine),
        "anim": MagicMock(spec=AnimationManager)
    }

@pytest.fixture
def orchestrator(mock_integrations):
    return ActionOrchestrator(
        github_integrator=mock_integrations["github"],
        jira_integrator=mock_integrations["jira"],
        llm_integrator=mock_integrations["llm"],
        policy_engine=mock_integrations["policy"],
        anim_manager=mock_integrations["anim"]
    )

def test_suggest_actions_no_github_context(orchestrator, mock_integrations):
    mock_integrations["github"].is_configured = False # Explicitly set to not configured
    mock_integrations["github"].get_pull_request_context.return_value = None
    
    result = orchestrator.suggest_actions(pr=123)
    
    assert result == []
    mock_integrations["anim"].fail.assert_called_once_with("GitHub integration is not configured. Cannot process GitHub-related options (--pr, --commit, --branch).")

def test_suggest_actions_github_jira_llm_success(orchestrator, mock_integrations):
    # Mock GitHub context
    mock_integrations["github"].is_configured = True
    mock_integrations["github"].get_pull_request_context.return_value = {
        "title": "Test PR", "message": "Test commit"
    }

    # Mock Jira issues
    mock_jira_issue = MagicMock()
    mock_jira_issue.key = "PROJ-1"
    mock_jira_issue.fields.summary = "Existing Jira Issue"
    mock_jira_issue.fields.description = "Description"
    mock_integrations["jira"].jira = True # Simulate successful Jira connection
    mock_integrations["jira"].search_issues.return_value = [mock_jira_issue]

    # Mock LLM suggestions
    mock_integrations["llm"].call_gemini.return_value = {
        "actions": [
            {"type": "use_existing_ticket", "issue_key": "PROJ-1", "similarity": 0.9, "reason": "Match"},
            {"type": "create_ticket", "summary": "New Ticket"}
        ]
    }

    # Mock Policy Engine
    mock_integrations["policy"].is_action_allowed.side_effect = lambda action_type: True
    mock_integrations["policy"].get_similarity_threshold.return_value = 0.7

    result = orchestrator.suggest_actions(pr=123)

    mock_integrations["anim"].start.assert_any_call("Loading GitHub context...")
    mock_integrations["anim"].succeed.assert_any_call("GitHub context loaded.")
    mock_integrations["anim"].start.assert_any_call("Searching Jira for similar tickets...")
    mock_integrations["anim"].succeed.assert_any_call("Found 1 potential Jira issue(s).")
    mock_integrations["anim"].start.assert_any_call("Asking the LLM for suggestions...")
    mock_integrations["anim"].succeed.assert_any_call("LLM analysis complete.")
    mock_integrations["anim"].start.assert_any_call("Applying policy rules...")
    mock_integrations["anim"].succeed.assert_any_call("Policy rules applied.")

    assert len(result) == 2
    assert result[0]["type"] == "use_existing_ticket"
    assert result[1]["type"] == "create_ticket"

def test_suggest_actions_llm_no_suggestions(orchestrator, mock_integrations):
    mock_integrations["github"].is_configured = True
    mock_integrations["github"].get_pull_request_context.return_value = {"title": "Test PR"}
    mock_integrations["jira"].jira = True
    mock_integrations["jira"].search_issues.return_value = []
    mock_integrations["llm"].call_gemini.return_value = {"actions": []}
    mock_integrations["policy"].is_action_allowed.return_value = True
    
    result = orchestrator.suggest_actions(pr=123)
    
    assert result == []
    mock_integrations["anim"].fail.assert_called_with("LLM did not provide any suggestions.")

def test_suggest_actions_policy_rejects_action(orchestrator, mock_integrations):
    mock_integrations["github"].is_configured = True
    mock_integrations["github"].get_pull_request_context.return_value = {"title": "Test PR"}
    mock_integrations["jira"].jira = True
    mock_integrations["jira"].search_issues.return_value = []
    mock_integrations["llm"].call_gemini.return_value = {
        "actions": [
            {"type": "malicious_action", "details": "exploit"}
        ]
    }
    mock_integrations["policy"].is_action_allowed.return_value = False # Policy rejects all actions
    mock_integrations["policy"].get_similarity_threshold.return_value = 0.7 # Not relevant here

    result = orchestrator.suggest_actions(pr=123)
    
    assert result == []
    mock_integrations["anim"].succeed.assert_called_with("Policy rules applied.") # Still succeeds applying rules
    mock_integrations["anim"].fail.assert_not_called() # No overall failure, just filtering
    # Verify that a message about rejection was echoed
    mock_integrations["anim"].succeed.assert_called_with("Policy rules applied.") # Still succeeds applying rules
    mock_integrations["anim"].fail.assert_not_called() # No overall failure, just filtering


# --- New tests for refactored execute_action and helper methods ---

def test_execute_action_create_ticket(orchestrator, mock_integrations):
    action = {"type": "create_ticket", "project": "PROJ", "summary": "Test Summary", "description": "Test Description"}
    mock_integrations["jira"].create_issue.return_value = MagicMock(key="PROJ-NEW")

    result = orchestrator.execute_action(action)
    assert result is True
    mock_integrations["jira"].create_issue.assert_called_once_with("PROJ", "Test Summary", "Test Description", "Task", None)
    mock_integrations["anim"].succeed.assert_called_once_with("Successfully created Jira ticket: PROJ-NEW")

def test_execute_action_create_ticket_failure(orchestrator, mock_integrations):
    action = {"type": "create_ticket", "project": "PROJ", "summary": "Test Summary", "description": "Test Description"}
    mock_integrations["jira"].create_issue.return_value = None

    result = orchestrator.execute_action(action)
    assert result is False
    mock_integrations["jira"].create_issue.assert_called_once_with("PROJ", "Test Summary", "Test Description", "Task", None)
    mock_integrations["anim"].fail.assert_called_once_with("Failed to create Jira ticket.")

def test_execute_action_transition_ticket_success(orchestrator, mock_integrations):
    action = {"type": "transition_ticket", "issue_key": "PROJ-1", "transition_name": "In Progress"}
    mock_integrations["jira"].get_issue_status.return_value = "OPEN"
    mock_integrations["policy"].is_transition_allowed.return_value = True
    mock_integrations["jira"].transition_issue.return_value = True

    result = orchestrator.execute_action(action)
    assert result is True
    mock_integrations["jira"].transition_issue.assert_called_once_with("PROJ-1", "In Progress")
    mock_integrations["anim"].succeed.assert_called_once_with("Successfully transitioned Jira ticket PROJ-1 to In Progress")

def test_execute_action_transition_ticket_policy_rejects(orchestrator, mock_integrations):
    action = {"type": "transition_ticket", "issue_key": "PROJ-1", "transition_name": "Done"}
    mock_integrations["jira"].get_issue_status.return_value = "IN PROGRESS"
    mock_integrations["policy"].is_transition_allowed.return_value = False

    result = orchestrator.execute_action(action)
    assert result is False
    mock_integrations["jira"].transition_issue.assert_not_called()
    mock_integrations["anim"].fail.assert_called_once_with("Policy: Transition from current status to 'Done' for PROJ-1 is not allowed.")

def test_execute_action_add_comment_success(orchestrator, mock_integrations):
    action = {"type": "add_comment", "issue_key": "PROJ-1", "comment_body": "New Comment"}
    mock_integrations["jira"].add_comment.return_value = MagicMock() # Any non-None value indicates success

    result = orchestrator.execute_action(action)
    assert result is True
    mock_integrations["jira"].add_comment.assert_called_once_with("PROJ-1", "New Comment")
    mock_integrations["anim"].succeed.assert_called_once_with("Successfully added comment to Jira ticket PROJ-1")

def test_execute_action_add_comment_failure(orchestrator, mock_integrations):
    action = {"type": "add_comment", "issue_key": "PROJ-1", "comment_body": "New Comment"}
    mock_integrations["jira"].add_comment.return_value = None

    result = orchestrator.execute_action(action)
    assert result is False
    mock_integrations["jira"].add_comment.assert_called_once_with("PROJ-1", "New Comment")
    mock_integrations["anim"].fail.assert_called_once_with("Failed to add comment to Jira ticket.")

def test_execute_action_use_existing_ticket(orchestrator, mock_integrations):
    action = {"type": "use_existing_ticket", "issue_key": "PROJ-1"}
    
    result = orchestrator.execute_action(action)
    assert result is True
    mock_integrations["anim"].succeed.assert_called_once_with("Acknowledged suggestion to use existing Jira ticket: PROJ-1")
    mock_integrations["jira"].create_issue.assert_not_called() # Ensure no API call

def test_execute_action_unknown_type(orchestrator, mock_integrations):
    action = {"type": "unknown_action", "data": "some data"}
    
    result = orchestrator.execute_action(action)
    assert result is False
    mock_integrations["anim"].fail.assert_called_once_with("Unknown action type: unknown_action")
    mock_integrations["jira"].create_issue.assert_not_called() # Ensure no API call