import click
import json
from typing import List, Dict, Any

from .github_integration import GitHubIntegration
from .jira_integration import JiraIntegration
from .llm_integration import LLMIntegration
from .policy_engine import PolicyEngine
from .ux import AnimationManager

class ActionOrchestrator:
    def __init__(self, github_integrator: GitHubIntegration, jira_integrator: JiraIntegration, 
                 llm_integrator: LLMIntegration, policy_engine: PolicyEngine, anim_manager: AnimationManager):
        self.github_integrator = github_integrator
        self.jira_integrator = jira_integrator
        self.llm_integrator = llm_integrator
        self.policy_engine = policy_engine
        self.anim = anim_manager

    def suggest_actions(self, pr: int = None, commit: str = None, branch: str = None) -> List[Dict[str, Any]]:
        """
        Orchestrates the process of gathering context, getting LLM suggestions,
        applying policy rules, and preparing actions for user approval.
        """
        # 1. Gather GitHub context
        self.anim.start("Loading GitHub context...")
        github_context = None
        if pr:
            github_context = self.github_integrator.get_pull_request_context(pr)
        elif commit:
            github_context = self.github_integrator.get_commit_context(commit)
        elif branch:
            github_context = self.github_integrator.get_branch_context(branch)

        if not github_context:
            self.anim.fail("Failed to retrieve GitHub context.")
            return []
        self.anim.succeed("GitHub context loaded.")

        # 2. Search Jira for similar tickets
        self.anim.start("Searching Jira for similar tickets...")
        jira_issues = []
        if self.jira_integrator.jira:
            search_query_text = github_context.get("title") or github_context.get("message")
            if search_query_text:
                search_query = f'text ~ "{search_query_text}"'
                jira_issues = self.jira_integrator.search_issues(search_query, max_results=5)
            self.anim.succeed(f"Found {len(jira_issues)} potential Jira issue(s).")
        else:
            self.anim.fail("Jira integration not configured. Skipping search.")

        # 3. Call LLM for analysis and suggestions
        self.anim.start("Asking the LLM for suggestions...")
        llm_prompt_data = {
            "github_context": github_context,
            "jira_issues_found": [{"key": issue.key, "summary": issue.fields.summary, "description": issue.fields.description} for issue in jira_issues],
            "request": "Propose Jira actions based on the provided context. Respond in the specified JSON format."
        }
        llm_prompt = json.dumps(llm_prompt_data)
        llm_suggestions = self.llm_integrator.call_gemini(llm_prompt)

        if not llm_suggestions or not llm_suggestions.get("actions"):
            self.anim.fail("LLM did not provide any suggestions.")
            return []
        self.anim.succeed("LLM analysis complete.")

        # 4. Apply policy to filter/validate LLM suggestions
        self.anim.start("Applying policy rules...")
        filtered_suggestions = self._apply_policy_rules(llm_suggestions)
        self.anim.succeed("Policy rules applied.")
        
        return filtered_suggestions

    def _apply_policy_rules(self, llm_suggestions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filters LLM suggestions based on configured policy rules.
        """
        if not llm_suggestions or not llm_suggestions.get("actions"):
            return []

        filtered_actions = []
        allowed_actions = self.policy_engine.get_allowed_actions()
        # TODO: Implement more granular policy checks (e.g., specific transitions, blocked states)

        for action in llm_suggestions["actions"]:
            action_type = action.get("type")
            if action_type and self.policy_engine.is_action_allowed(action_type):
                # Placeholder for more complex policy validation
                # e.g., validate transition based on allowed_transitions, check blocked_states
                if action_type == "use_existing_ticket":
                    if action.get("similarity", 0) >= self.policy_engine.get_similarity_threshold():
                        filtered_actions.append(action)
                    else:
                        click.echo(f"Policy: Rejecting 'use_existing_ticket' due to low similarity ({action.get('similarity', 0)} < {self.policy_engine.get_similarity_threshold()}).", err=True)
                else:
                    filtered_actions.append(action)
            else:
                click.echo(f"Policy: Rejecting action type '{action_type}' as it is not allowed by policy.", err=True)
        return filtered_actions

    def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Executes a given action.
        """
        action_type = action.get("type")
        if action_type == "create_ticket":
            project = action.get("project", "YOUR_DEFAULT_JIRA_PROJECT") # TODO: Make configurable
            summary = action.get("summary")
            description = action.get("description")
            issue_type = action.get("issue_type", "Task")
            labels = action.get("labels")
            if summary and description:
                new_issue = self.jira_integrator.create_issue(project, summary, description, issue_type, labels)
                if new_issue:
                    click.echo(f"Successfully created Jira ticket: {new_issue.key}", fg='green')
                    return True
            click.echo("Failed to create Jira ticket.", fg='red')
            return False
        elif action_type == "transition_ticket":
            issue_key = action.get("issue_key")
            transition_name = action.get("transition_name")
            if issue_key and transition_name:
                if self.policy_engine.is_transition_allowed(self.jira_integrator.get_issue_status(issue_key), transition_name): # Need to get current status first
                    if self.jira_integrator.transition_issue(issue_key, transition_name):
                        click.echo(f"Successfully transitioned Jira ticket {issue_key} to {transition_name}", fg='green')
                        return True
                else:
                    click.echo(f"Policy: Transition from current status to '{transition_name}' for {issue_key} is not allowed.", fg='red')
            click.echo("Failed to transition Jira ticket.", fg='red')
            return False
        elif action_type == "add_comment":
            issue_key = action.get("issue_key")
            comment_body = action.get("comment_body")
            if issue_key and comment_body:
                if self.jira_integrator.add_comment(issue_key, comment_body):
                    click.echo(f"Successfully added comment to Jira ticket {issue_key}", fg='green')
                    return True
            click.echo("Failed to add comment to Jira ticket.", fg='red')
            return False
        elif action_type == "use_existing_ticket":
            issue_key = action.get("issue_key")
            click.echo(f"Acknowledged suggestion to use existing Jira ticket: {issue_key}", fg='cyan')
            return True # This action type is just a suggestion, no execution needed.
        else:
            click.echo(f"Unknown action type: {action_type}", fg='red')
            return False

    def present_and_execute_actions(self, suggested_actions: List[Dict[str, Any]]):
        """
        Presents suggested actions to the user for approval and executes them if approved.
        """
        if not suggested_actions:
            click.echo("No actions to present.", fg='yellow')
            return

        click.echo("\n--- Proposed Jira Actions ---")
        for i, action in enumerate(suggested_actions):
            click.echo(f"\nAction {i+1} (Type: {action.get('type')}):")
            click.echo(json.dumps(action, indent=2))
            
            # Simple editing mechanism
            edit_choice = click.prompt("Do you want to edit this action? (y/N)", default="n").lower()
            if edit_choice == 'y':
                edited_json = click.edit(json.dumps(action, indent=2))
                if edited_json:
                    try:
                        action = json.loads(edited_json)
                        click.echo("Action updated after editing.")
                    except json.JSONDecodeError:
                        click.echo("Invalid JSON provided. Using original action.", fg='red')

            if action.get("type") == "use_existing_ticket":
                # For 'use_existing_ticket', it's a suggestion, not an execution.
                # We simply acknowledge it.
                if click.confirm(f"Acknowledge suggestion to use existing ticket {action.get('issue_key')}?"):
                    self.execute_action(action) # Will just print acknowledgment
                else:
                    click.echo("Suggestion to use existing ticket rejected.")
            else:
                if click.confirm("Approve this action for execution?"):
                    self.execute_action(action)
                else:
                    click.echo("Action rejected by user.")
        click.echo("\n--- End of Proposed Actions ---")
