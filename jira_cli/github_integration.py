import os
import requests
import click
from .config_manager import ConfigManager

GITHUB_API_URL = "https://api.github.com"

class GitHubIntegration:
    def __init__(self):
        config_manager = ConfigManager()
        config = config_manager.load_config()

        self.github_token = config.get("GITHUB_TOKEN")
        self.owner = config.get("GITHUB_OWNER")
        self.repo = config.get("GITHUB_REPO")

        if not all([self.github_token, self.owner, self.repo]):
            self.github_token = None # Explicitly set to None if incomplete
            self.owner = None
            self.repo = None
            self.headers = {} # Empty headers if not configured
            # No error message here, as it's now optional. Orchestrator will handle.
        else:
            self.headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
    
    @property
    def is_configured(self):
        return all([self.github_token, self.owner, self.repo])

    def _make_request(self, method, path, params=None):
        if not self.is_configured:
            click.echo("GitHub integration is not configured. Skipping API request.", err=True)
            return None

        url = f"{GITHUB_API_URL}/repos/{self.owner}/{self.repo}/{path}"
        try:
            response = requests.request(method, url, headers=self.headers, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            click.echo(f"GitHub API Error: {e}", err=True)
            return None

    def get_pull_request_context(self, pr_number):
        """
        Fetches context for a given Pull Request.
        Returns PR title, description, and related commit messages.
        """
        if not self.is_configured:
            click.echo("GitHub integration is not configured. Cannot get PR context.", err=True)
            return None
        
        click.echo(f"Fetching PR context for PR #{pr_number}...")
        pr_data = self._make_request("GET", f"pulls/{pr_number}")
        if not pr_data:
            return None

        title = pr_data.get("title")
        description = pr_data.get("body")

        commits_data = self._make_request("GET", f"pulls/{pr_number}/commits")
        commit_messages = []
        if commits_data:
            for commit in commits_data:
                commit_messages.append(commit["commit"]["message"])
        
        return {
            "type": "pull_request",
            "pr_number": pr_number,
            "title": title,
            "description": description,
            "commit_messages": commit_messages,
        }

    def get_commit_context(self, commit_sha):
        """
        Fetches context for a given Commit.
        Returns commit message.
        """
        if not self.is_configured:
            click.echo("GitHub integration is not configured. Cannot get commit context.", err=True)
            return None

        click.echo(f"Fetching commit context for SHA: {commit_sha}...")
        commit_data = self._make_request("GET", f"commits/{commit_sha}")
        if not commit_data:
            return None
        
        return {
            "type": "commit",
            "commit_sha": commit_sha,
            "message": commit_data["commit"]["message"],
        }

    def get_branch_context(self, branch_name):
        """
        Fetches context for a given Branch.
        For simplicity, this might just get the latest commit on the branch.
        """
        if not self.is_configured:
            click.echo("GitHub integration is not configured. Cannot get branch context.", err=True)
            return None

        click.echo(f"Fetching branch context for branch: {branch_name}...")
        branch_data = self._make_request("GET", f"branches/{branch_name}")
        if not branch_data:
            return None
        
        latest_commit_sha = branch_data["commit"]["sha"]
        # For a full context, you might want to get the commit message of the latest commit
        commit_context = self.get_commit_context(latest_commit_sha)
        
        return {
            "type": "branch",
            "branch_name": branch_name,
            "latest_commit_sha": latest_commit_sha,
            "latest_commit_message": commit_context["message"] if commit_context else None,
        }
