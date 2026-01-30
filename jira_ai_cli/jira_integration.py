import os
from jira import JIRA
import click
from .config_manager import ConfigManager

class JiraIntegration:
    def __init__(self):
        config_manager = ConfigManager()
        config = config_manager.load_config()

        self.jira_server = config.get("JIRA_SERVER")
        self.jira_username = config.get("JIRA_USERNAME")
        self.jira_api_token = config.get("JIRA_API_TOKEN")

        if not all([self.jira_server, self.jira_username, self.jira_api_token]):
            click.echo("Error: Jira configuration not found. Please run 'jira-ai config' to set up your credentials.", err=True)
            self.jira = None
            return

        try:
            self.jira = JIRA(
                server=self.jira_server,
                basic_auth=(self.jira_username, self.jira_api_token)
            )
            click.echo("Successfully connected to Jira.", err=False) # Log success for debugging
        except Exception as e:
            click.echo(f"Error connecting to Jira: {e}", err=True)
            self.jira = None
    
    def get_issue_status(self, issue_key: str) -> str:
        """
        Retrieves the status of a Jira issue.
        """
        if not self.jira:
            return ""
        try:
            issue = self.jira.issue(issue_key)
            return issue.fields.status.name
        except Exception as e:
            click.echo(f"Error getting status for issue {issue_key}: {e}", err=True)
            return ""

    def search_issues(self, jql_query, max_results=5):
        """
        Searches Jira issues using a JQL query.
        Returns a list of issue objects.
        """
        if not self.jira:
            return [] # Return empty list if Jira is not initialized
        click.echo(f"Searching Jira with JQL: {jql_query}", err=False)
        try:
            issues = self.jira.search_issues(jql_query, maxResults=max_results)
            return issues
        except Exception as e:
            click.echo(f"Error searching Jira issues: {e}", err=True)
            return [] # Return empty list on error

    def create_issue(self, project, summary, description, issue_type="Task", labels=None):
        """
        Creates a new Jira issue.
        Returns the created issue object.
        """
        if not self.jira:
            return None
        click.echo(f"Creating Jira issue in project {project} with summary: {summary}", err=False)
        issue_dict = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }
        if labels:
            issue_dict['labels'] = labels
        try:
            new_issue = self.jira.create_issue(fields=issue_dict)
            return new_issue
        except Exception as e:
            click.echo(f"Error creating Jira issue: {e}", err=True)
            return None

    def transition_issue(self, issue_key, transition_name):
        """
        Transitions a Jira issue to a new status.
        Returns True on success, False otherwise.
        """
        if not self.jira:
            return False
        click.echo(f"Transitioning issue {issue_key} to: {transition_name}", err=False)
        try:
            issue = self.jira.issue(issue_key)
            transitions = self.jira.transitions(issue)
            transition_id = None
            for t in transitions:
                if t['name'] == transition_name:
                    transition_id = t['id']
                    break
            
            if transition_id:
                self.jira.transition_issue(issue, transition_id)
                return True
            else:
                click.echo(f"Error: Transition '{transition_name}' not found for issue {issue_key}.", err=True)
                return False
        except Exception as e:
            click.echo(f"Error transitioning Jira issue {issue_key}: {e}", err=True)
            return False

    def add_comment(self, issue_key, comment_body):
        """
        Adds a comment to a Jira issue.
        Returns the created comment object.
        """
        if not self.jira:
            return None
        click.echo(f"Adding comment to issue {issue_key}", err=False)
        try:
            new_comment = self.jira.add_comment(issue_key, comment_body)
            return new_comment
        except Exception as e:
            click.echo(f"Error adding comment to Jira issue {issue_key}: {e}", err=True)
            return None
