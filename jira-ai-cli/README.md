# LLM-Assisted Jira CLI

This CLI tool helps developers interact with Jira directly from the command line, using an LLM (like Gemini) to assist with reasoning and ticket creation.

## Prerequisites

- Python 3.7+
- `pip` and `git`

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd jira-ai-cli
    ```

2.  **Install the CLI:**

    Install the package using `pip`. This command will also install all the required dependencies (`click`, `requests`, `jira`, etc.) and make the `jira-ai` command available in your terminal.

    ```bash
    pip install .
    ```

    *Note: If you are actively developing the CLI, you can install it in "editable" mode with `pip install -e .`. This allows your changes to the source code to be immediately reflected when you run the `jira-ai` command.*

## Configuration

After installation, you need to configure the CLI with your Jira and GitHub credentials. The CLI includes an interactive command to guide you through this setup.

1.  **Run the `config` command:**

    ```bash
    jira-ai config
    ```

2.  **Provide your credentials:**

    The tool will prompt you for the following information:
    - Your Jira Server URL (e.g., `https://your-domain.atlassian.net`)
    - Your Jira Username (the email you use to log in)
    - Your Jira API Token (this can be generated from your Atlassian account settings)
    - Your GitHub Repository Owner (the organization or username that owns the repo)
    - Your GitHub Repository Name
    - Your GitHub Personal Access Token (with `repo` scope)

    Your credentials will be stored locally in `~/.jira-ai-cli/config.json`.

## Usage

Once the CLI is installed and configured, you can start using it. For example, to get suggestions for a pull request:

```bash
jira-ai suggest --pr 123
```

Or for a specific branch:

```bash
jira-ai suggest --branch feature/login-flow
```
