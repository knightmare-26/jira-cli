import click
import json
from .github_integration import GitHubIntegration
from .jira_integration import JiraIntegration
from .llm_integration import LLMIntegration
from .policy_engine import PolicyEngine
from .action_orchestrator import ActionOrchestrator
from .config_manager import ConfigManager

@click.group()
def cli():
    """LLM-Assisted Jira CLI"""
    pass

@cli.command()
def config():
    """
    Guides the user through setting up the required configurations for Jira and GitHub.
    """
    config_manager = ConfigManager()
    existing_config = config_manager.load_config()

    click.echo("--- Jira Configuration ---")
    jira_server = click.prompt("Jira Server URL (e.g., https://your-domain.atlassian.net)", default=existing_config.get("JIRA_SERVER"))
    jira_username = click.prompt("Jira Username (email)", default=existing_config.get("JIRA_USERNAME"))
    jira_api_token = click.prompt("Jira API Token", default=existing_config.get("JIRA_API_TOKEN"), hide_input=True)

    click.echo("\n--- GitHub Configuration ---")
    github_owner = click.prompt("GitHub Repository Owner (organization or user)", default=existing_config.get("GITHUB_OWNER"))
    github_repo = click.prompt("GitHub Repository Name", default=existing_config.get("GITHUB_REPO"))
    github_token = click.prompt("GitHub Personal Access Token", default=existing_config.get("GITHUB_TOKEN"), hide_input=True)

    new_config = {
        "JIRA_SERVER": jira_server,
        "JIRA_USERNAME": jira_username,
        "JIRA_API_TOKEN": jira_api_token,
        "GITHUB_OWNER": github_owner,
        "GITHUB_REPO": github_repo,
        "GITHUB_TOKEN": github_token,
    }
    
    config_manager.save_config(new_config)


@cli.command()
@click.option('--pr', type=int, help='GitHub Pull Request number.')
@click.option('--commit', type=str, help='GitHub Commit reference (SHA).')
@click.option('--branch', type=str, help='GitHub Branch name.')
def suggest(pr, commit, branch):
    """
    Suggests Jira actions based on GitHub context.
    """
    # Ensure only one of --pr, --commit, or --branch is provided
    provided_options = sum([1 for x in [pr, commit, branch] if x is not None])
    if provided_options > 1:
        click.echo("Error: Please provide only one of --pr, --commit, or --branch.", err=True)
        return
    elif provided_options == 0:
        click.echo("Error: Please provide at least one of --pr, --commit, or --branch.", err=True)
        return

    # Initialize all components
    github_integrator = GitHubIntegration()
    jira_integrator = JiraIntegration()
    llm_integrator = LLMIntegration()
    policy_engine = PolicyEngine(policy_file_path="jira-ai-cli/policy.yaml") # Specify path relative to project root

    # Policy Engine Integration (Moved here to always show policy)
    click.echo("\n--- Policy Engine Integration ---")
    click.echo(f"Allowed actions: {policy_engine.get_allowed_actions()}")
    click.echo(f"Min similarity: {policy_engine.get_similarity_threshold()}")
    click.echo("---------------------------------")
    
    # Initialize and run the Action Orchestrator
    orchestrator = ActionOrchestrator(
        github_integrator=github_integrator,
        jira_integrator=jira_integrator,
        llm_integrator=llm_integrator,
        policy_engine=policy_engine
    )

    suggested_actions = orchestrator.suggest_actions(pr=pr, commit=commit, branch=branch)

    if suggested_actions:
        orchestrator.present_and_execute_actions(suggested_actions)
    else:
        click.echo("Orchestrator did not suggest any actions after applying policies.", err=True)

if __name__ == '__main__':
    cli()
