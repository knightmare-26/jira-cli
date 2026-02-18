import click
import json
from importlib.metadata import version
from .github_integration import GitHubIntegration
from .jira_integration import JiraIntegration
from .llm_integration import LLMIntegration
from .policy_engine import PolicyEngine
from .action_orchestrator import ActionOrchestrator
from .config_manager import ConfigManager
from .ux import AnimationManager

@click.group()
@click.version_option(version=version("jira-ai-cli"))
def cli():
    """LLM-Assisted Jira CLI"""
    pass

@cli.command()
def config():
    """
    Guides the user through setting up the required configurations for Jira, GitHub, and LLM.
    """
    config_manager = ConfigManager()
    existing_config = config_manager.load_config()

    click.echo("--- Jira Configuration ---")
    jira_server = click.prompt("Jira Server URL (e.g., https://your-domain.atlassian.net)", default=existing_config.get("JIRA_SERVER"))
    jira_username = click.prompt("Jira Username (email)", default=existing_config.get("JIRA_USERNAME"))
    jira_api_token = click.prompt("Jira API Token", default=existing_config.get("JIRA_API_TOKEN"), hide_input=True)

    click.echo("\n--- GitHub Configuration (Optional) ---")
    configure_github = click.confirm("Do you want to configure GitHub integration? (This is only required if you plan to use --pr, --commit, or --branch options)", default=False)

    github_owner = None
    github_repo = None
    github_token = None

    if configure_github:
        github_owner = click.prompt("GitHub Repository Owner (organization or user)", default=existing_config.get("GITHUB_OWNER"))
        github_repo = click.prompt("GitHub Repository Name", default=existing_config.get("GITHUB_REPO"))
        github_token = click.prompt("GitHub Personal Access Token", default=existing_config.get("GITHUB_TOKEN"), hide_input=True)
    else:
        click.echo("Skipping GitHub configuration.")

    click.echo("\n--- LLM Configuration ---")
    llm_provider = click.prompt(
        "LLM Provider",
        type=click.Choice(['gemini-cli', 'openai', 'anthropic', 'gemini', 'custom-cli'], case_sensitive=False),
        default=existing_config.get("LLM_PROVIDER", "gemini-cli")
    )

    llm_model = None
    llm_api_key = None
    llm_custom_command = None

    if llm_provider == 'gemini-cli':
        click.echo("Using the local 'gemini' CLI tool.")
    elif llm_provider == 'custom-cli':
        llm_custom_command = click.prompt("Custom CLI Command (use {prompt} as placeholder)", default=existing_config.get("LLM_CUSTOM_COMMAND", "echo '{prompt}'"))
    else:
        # For openai, anthropic, gemini (via API)
        default_model = {
            'openai': 'gpt-4o',
            'anthropic': 'claude-3-5-sonnet-20240620',
            'gemini': 'gemini-1.5-pro'
        }.get(llm_provider)
        
        llm_model = click.prompt(f"{llm_provider.capitalize()} Model", default=existing_config.get("LLM_MODEL", default_model))
        llm_api_key = click.prompt(f"{llm_provider.capitalize()} API Key", default=existing_config.get("LLM_API_KEY"), hide_input=True)

    new_config = {
        "JIRA_SERVER": jira_server,
        "JIRA_USERNAME": jira_username,
        "JIRA_API_TOKEN": jira_api_token,
        "GITHUB_OWNER": github_owner,
        "GITHUB_REPO": github_repo,
        "GITHUB_TOKEN": github_token,
        "LLM_PROVIDER": llm_provider,
        "LLM_MODEL": llm_model,
        "LLM_API_KEY": llm_api_key,
        "LLM_CUSTOM_COMMAND": llm_custom_command
    }
    
    config_manager.save_config(new_config)


@cli.command()
@click.option('--pr', type=int, help='GitHub Pull Request number.')
@click.option('--commit', type=str, help='GitHub Commit reference (SHA).')
@click.option('--branch', type=str, help='GitHub Branch name.')
@click.option('--no-animation', is_flag=True, help='Disables CLI animations and spinners.')
def suggest(pr, commit, branch, no_animation):
    """
    Suggests Jira actions based on GitHub context.
    """
    anim_manager = AnimationManager(no_animation=no_animation)
    anim_manager.show_banner()

    # Ensure only one of --pr, --commit, or --branch is provided
    provided_options = sum([1 for x in [pr, commit, branch] if x is not None])
    if provided_options > 1:
        anim_manager.fail("Error: Please provide only one of --pr, --commit, or --branch.")
        raise click.Abort()
    elif provided_options == 0:
        anim_manager.fail("Error: Please provide at least one of --pr, --commit, or --branch.")
        raise click.Abort()

    # Initialize all components
    github_integrator = GitHubIntegration()
    jira_integrator = JiraIntegration()
    llm_integrator = LLMIntegration()
    policy_engine = PolicyEngine(policy_file_path="jira-ai-cli/policy.yaml") # Specify path relative to project root
    
    # Initialize and run the Action Orchestrator
    orchestrator = ActionOrchestrator(
        github_integrator=github_integrator,
        jira_integrator=jira_integrator,
        llm_integrator=llm_integrator,
        policy_engine=policy_engine,
        anim_manager=anim_manager
    )

    suggested_actions = orchestrator.suggest_actions(pr=pr, commit=commit, branch=branch)

    if suggested_actions:
        orchestrator.present_and_execute_actions(suggested_actions)
    else:
        anim_manager.fail("Orchestrator did not suggest any actions after applying policies.")

if __name__ == '__main__':
    cli()
