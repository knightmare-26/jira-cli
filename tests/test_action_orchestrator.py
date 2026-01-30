import pytest
import json # Added import
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
    mock_integrations["github"].get_pull_request_context.return_value = None
    
    result = orchestrator.suggest_actions(pr=123)
    
    assert result == []
    mock_integrations["anim"].fail.assert_called_once_with("Failed to retrieve GitHub context.")

def test_suggest_actions_github_jira_llm_success(orchestrator, mock_integrations):
    # Mock GitHub context
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
    mock_integrations["github"].get_pull_request_context.return_value = {"title": "Test PR"}
    mock_integrations["jira"].jira = True
    mock_integrations["jira"].search_issues.return_value = []
    mock_integrations["llm"].call_gemini.return_value = {"actions": []}
    mock_integrations["policy"].is_action_allowed.return_value = True
    
    result = orchestrator.suggest_actions(pr=123)
    
    assert result == []
    mock_integrations["anim"].fail.assert_called_with("LLM did not provide any suggestions.")

def test_suggest_actions_policy_rejects_action(orchestrator, mock_integrations):
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

@patch('click.prompt')
@patch('click.confirm')
@patch('click.edit')
def test_present_and_execute_actions_create_ticket(mock_edit, mock_confirm, mock_prompt, orchestrator, mock_integrations):
    suggested_actions = [{"type": "create_ticket", "project": "PROJ", "summary": "New Task", "description": "Details"}]
    mock_confirm.return_value = True # User approves
    mock_integrations["jira"].create_issue.return_value = MagicMock(key="PROJ-NEW")

    orchestrator.present_and_execute_actions(suggested_actions)

    mock_integrations["jira"].create_issue.assert_called_once_with("PROJ", "New Task", "Details", "Task", None)
    mock_integrations["anim"].succeed.assert_any_call("Successfully created Jira ticket: PROJ-NEW")

@patch('click.prompt')
@patch('click.confirm')
@patch('click.edit')
def test_present_and_execute_actions_transition_ticket_approved(mock_edit, mock_confirm, mock_prompt, orchestrator, mock_integrations):
    suggested_actions = [{"type": "transition_ticket", "issue_key": "PROJ-1", "transition_name": "In Progress"}]
    mock_confirm.return_value = True # User approves
    mock_integrations["jira"].get_issue_status.return_value = "OPEN"
    mock_integrations["policy"].is_transition_allowed.return_value = True
    mock_integrations["jira"].transition_issue.return_value = True

    orchestrator.present_and_execute_actions(suggested_actions)

    mock_integrations["jira"].transition_issue.assert_called_once_with("PROJ-1", "In Progress")
    mock_integrations["anim"].succeed.assert_any_call("Successfully transitioned Jira ticket PROJ-1 to In Progress")

@patch('click.prompt')
@patch('click.confirm')
@patch('click.edit')
def test_present_and_execute_actions_transition_ticket_policy_rejects(mock_edit, mock_confirm, mock_prompt, orchestrator, mock_integrations):
    suggested_actions = [{"type": "transition_ticket", "issue_key": "PROJ-1", "transition_name": "Done"}]
    mock_confirm.return_value = True # User approves
    mock_integrations["jira"].get_issue_status.return_value = "IN PROGRESS"
    mock_integrations["policy"].is_transition_allowed.return_value = False # Policy rejects

    orchestrator.present_and_execute_actions(suggested_actions)

    mock_integrations["jira"].transition_issue.assert_not_called()
    mock_integrations["anim"].fail.assert_any_call("Policy: Transition from current status to 'Done' for PROJ-1 is not allowed.")

@patch('click.prompt')
@patch('click.confirm')
@patch('click.edit')
def test_present_and_execute_actions_edit_action(mock_edit, mock_confirm, mock_prompt, orchestrator, mock_integrations):
    original_action = {"type": "create_ticket", "project": "PROJ", "summary": "Original Summary"}
    edited_action = {"type": "create_ticket", "project": "PROJ", "summary": "Edited Summary", "description": "New Desc"}
    suggested_actions = [original_action]

    mock_prompt.return_value = "y" # User chooses to edit
    mock_edit.return_value = json.dumps(edited_action) # User provides edited JSON
    mock_confirm.return_value = True # User approves edited action

    mock_integrations["jira"].create_issue.return_value = MagicMock(key="PROJ-EDITED")

    orchestrator.present_and_execute_actions(suggested_actions)

    mock_integrations["jira"].create_issue.assert_called_once_with("PROJ", "Edited Summary", "New Desc", "Task", None)
    mock_integrations["anim"].succeed.assert_any_call("Successfully created Jira ticket: PROJ-EDITED")
