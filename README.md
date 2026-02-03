# Aera Jira AI CLI: Your Smart Command-Line Assistant for Jira

Tired of manually creating Jira tickets from your GitHub activity? The Aera Jira AI CLI is a smart tool that helps you manage your Jira projects directly from your command line, using the power of AI to streamline your workflow.

## What Can It Do?

-   **Analyze Your Work**: It looks at your GitHub pull requests, commits, or branches.
-   **Suggest Actions**: It suggests relevant Jira actions, like creating a new ticket or updating an existing one.
-   **Automate Tedious Tasks**: It can create tickets, add comments, and transition issues for you, saving you time and effort.

## Installation and Setup Guide

This guide will walk you through setting up and using the Aera Jira AI CLI.

### Step 1: Prerequisites

Before you begin, you'll need a couple of things:

-   **A Terminal**: This is the command-line interface on your computer. On macOS, you can use the "Terminal" app. On Windows, you can use "PowerShell" or "Command Prompt".
-   **Git**: A tool for downloading files from GitHub. If you don't have it, you can [download it here](https://git-scm.com/downloads).
-   **Gemini CLI**: For the AI functionality, you need the `gemini` command-line tool installed and configured on your system. Follow the official Gemini documentation to set it up.

### Step 2: Install the Aera Jira AI CLI

You have two main options for installation:

#### A. Binary Installation (Recommended for most users)

This is the easiest way to get started as it doesn't require Python or other dependencies.

1.  **Download the executable:**
    Go to the [GitHub Releases page](https://github.com/elijahdsouza-aera/jira-cli/releases) and download the appropriate file for your operating system:
    *   **Linux:** `Aera-Jira-CLI-linux`
    *   **macOS:** `Aera-Jira-CLI-macos`
    *   **Windows:** `Aera-Jira-CLI-windows.exe`

2.  **Place the executable in your PATH:**
    Move the downloaded file to a directory that is included in your system's `PATH`. Common locations are `/usr/local/bin` (Linux/macOS) or a custom `bin` directory that you've added to your Windows `PATH` environment variable. This allows you to run the command from any directory.

3.  **Ensure executable permissions (Linux/macOS only):**
    Open your terminal, navigate to where you saved the file, and run:
    ```bash
    chmod +x /path/to/Aera-Jira-CLI-macos # or -linux
    ```

#### B. Source Installation (for Developers)

If you plan to contribute to the project or prefer to run directly from Python source, follow these steps:

1.  **Clone the repository:**
    Open your terminal and run:
    ```bash
    git clone https://github.com/elijahdsouza-aera/jira-cli.git
    cd jira-cli
    ```
2.  **Install the CLI:**
    Install the package using `pip`. This command will also install all the required Python dependencies.
    ```bash
    pip install .
    ```
    If you are actively developing, you can install in "editable" mode:
    ```bash
    pip install -e .
    ```

### Step 3: Configure Your Credentials

To connect to Jira and GitHub, the CLI needs your credentials. Don't worry, they are stored securely on your local machine.

1.  Run the configuration command:

    ```bash
    Aera-Jira-CLI config
    ```
    If you installed from source, you'll use `jira-cli config` instead.

2.  The tool will then prompt you for the following information:

    -   **Jira Server URL**: The web address of your Jira instance (e.g., `https://your-company.atlassian.net`).
    -   **Jira Username**: The email address you use to log in to Jira.
    -   **Jira API Token**: This is like a password for applications. You can create one by following [Atlassian's guide](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).
    -   **GitHub Repository Owner**: The username or organization that owns the GitHub repository (e.g., `elijahdsouza-aera`).
    -   **GitHub Repository Name**: The name of the repository (e.g., `jira-cli`).
    -   **GitHub Personal Access Token**: This is like a password for applications to access GitHub. You can create one by following [GitHub's guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). Make sure to give it the `repo` scope.

### Step 4: Start Using the CLI!

You're all set! Now you can start using the Aera Jira AI CLI to manage your projects.

**Example: Get Suggestions for a Pull Request**

Let's say you've just created a pull request with the number 123. You can ask the CLI for suggestions like this:

```bash
Aera-Jira-CLI suggest --pr 123
```
If you installed from source, you'll use `jira-cli suggest --pr 123` instead.

The CLI will analyze the pull request and suggest relevant Jira actions. You can then approve or reject these suggestions.

**Other Examples:**

You can also get suggestions for a specific commit or branch:

```bash
# Get suggestions for a commit
Aera-Jira-CLI suggest --commit <commit_sha>

# Get suggestions for a branch
Aera-Jira-CLI suggest --branch <branch_name>
```

---

We hope you enjoy using the Aera Jira AI CLI! If you have any questions or feedback, please feel free to open an issue on the [GitHub repository](https://github.com/elijahdsouza-aera/jira-cli/issues).