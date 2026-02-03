# Jira AI CLI: Your Smart Command-Line Assistant for Jira

Tired of manually creating Jira tickets from your GitHub activity? The Jira AI CLI is a smart tool that helps you manage your Jira projects directly from your command line, using the power of AI to streamline your workflow.

## What Can It Do?

-   **Analyze Your Work**: It looks at your GitHub pull requests, commits, or branches.
-   **Suggest Actions**: It suggests relevant Jira actions, like creating a new ticket or updating an existing one.
-   **Automate Tedious Tasks**: It can create tickets, add comments, and transition issues for you, saving you time and effort.

## Installation and Setup Guide

This guide will walk you through setting up and using the Jira AI CLI.

### Step 1: Prerequisites

Before you begin, you'll need a couple of things:

-   **A Terminal**: This is the command-line interface on your computer. On macOS, you can use the "Terminal" app. On Windows, you can use "PowerShell" or "Command Prompt".
-   **Git**: A tool for downloading files from GitHub. If you don't have it, you can [download it here](https://git-scm.com/downloads).

### Step 2: Download the Project

1.  Open your terminal.
2.  Navigate to the directory where you want to save the project.
3.  Run the following command to download the project files from GitHub:

    ```bash
    git clone https://github.com/elijahdsouza-aera/jira-cli.git
    ```

4.  Navigate into the newly created directory:

    ```bash
    cd jira-cli
    ```

### Step 3: Install the CLI

Now, you'll install the Jira AI CLI and its dependencies.

1.  Make sure you have Python installed. You can check by running `python --version` or `python3 --version`. If you don't have it, you can [download it here](https://www.python.org/downloads/).
2.  Install the CLI using pip (Python's package installer):

    ```bash
    pip install .
    ```
    If you're using Python 3, you might need to use `pip3`:
    ```bash
    pip3 install .
    ```

### Step 4: Configure Your Credentials

To connect to Jira and GitHub, the CLI needs your credentials. Don't worry, they are stored securely on your local machine.

1.  Run the configuration command:

    ```bash
    jira-cli config
    ```
    If you installed with `pip3`, you might need to run `jira-cli` like this: `python3 -m jira_ai_cli.cli config`

2.  The tool will then prompt you for the following information:

    -   **Jira Server URL**: The web address of your Jira instance (e.g., `https://your-company.atlassian.net`).
    -   **Jira Username**: The email address you use to log in to Jira.
    -   **Jira API Token**: This is like a password for applications. You can create one by following [Atlassian's guide](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).
    -   **GitHub Repository Owner**: The username or organization that owns the GitHub repository (e.g., `elijahdsouza-aera`).
    -   **GitHub Repository Name**: The name of the repository (e.g., `jira-cli`).
    -   **GitHub Personal Access Token**: This is like a password for applications to access GitHub. You can create one by following [GitHub's guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). Make sure to give it the `repo` scope.

### Step 5: Start Using the CLI!

You're all set! Now you can start using the Jira AI CLI to manage your projects.

**Example: Get Suggestions for a Pull Request**

Let's say you've just created a pull request with the number 123. You can ask the CLI for suggestions like this:

```bash
jira-cli suggest --pr 123
```

The CLI will analyze the pull request and suggest relevant Jira actions. You can then approve or reject these suggestions.

**Other Examples:**

You can also get suggestions for a specific commit or branch:

```bash
# Get suggestions for a commit
jira-cli suggest --commit <commit_sha>

# Get suggestions for a branch
jira-cli suggest --branch <branch_name>
```

---

We hope you enjoy using the Jira AI CLI! If you have any questions or feedback, please feel free to open an issue on the [GitHub repository](https://github.com/elijahdsouza-aera/jira-cli/issues).
