# Aera Jira AI CLI

The Aera Jira AI CLI is a powerful command-line interface designed to streamline Jira workflow management through AI assistance. It integrates seamlessly with GitHub to automate tasks and provide intelligent suggestions, enhancing developer productivity.

## Key Features

-   **Contextual Analysis**: Analyzes GitHub pull requests, commits, and branches to understand development context.
-   **Intelligent Suggestions**: Provides AI-driven recommendations for Jira actions, including ticket creation and updates.
-   **Automated Workflow**: Facilitates the automated creation, commenting, and transitioning of Jira issues.

## Prerequisites

To effectively utilize the Aera Jira AI CLI, the following external tools must be installed and accessible on your system:

-   **Terminal Access**: A command-line interpreter (e.g., PowerShell, Command Prompt on Windows; Terminal on macOS/Linux).
-   **Git**: A version control system essential for repository operations. Download Git from [git-scm.com/downloads](https://git-scm.com/downloads).
-   **Gemini CLI**: The official Gemini command-line tool is required for AI functionality and communication with the Gemini AI model. Refer to the [official Gemini documentation](https://ai.google.dev/gemini-api/docs/get-started/python) for installation and configuration instructions.

## Installation

The Aera Jira AI CLI offers two primary installation methods:

### A. Binary Installation (Recommended)

This method provides a standalone executable, eliminating the need for Python or other language-specific dependencies.

1.  **Download the Executable:**
    Access the [GitHub Releases page](https://github.com/elijahdsouza-aera/jira-cli/releases) to download the pre-compiled binary. The Releases page is recommended as it facilitates the selection of the correct executable for your operating system (Linux, macOS, or Windows) and provides associated release information.
    *   **Linux:** `Aera-Jira-CLI-linux`
    *   **macOS:** `Aera-Jira-CLI-macos`
    *   **Windows:** `Aera-Jira-CLI-windows.exe`

2.  **Add to System PATH:**
    Relocate the downloaded executable to a directory included in your system's `PATH` environment variable. This enables execution of the CLI from any terminal location.
    *   **Typical locations:** `/usr/local/bin` (Linux/macOS) or a designated `bin` directory (Windows).

3.  **Set Executable Permissions (Linux/macOS only):**
    Execute the following command in your terminal to grant execution privileges:
    ```bash
    chmod +x /path/to/Aera-Jira-CLI-macos # or -linux
    ```

### B. Source Installation

This method is suitable for developers, contributors, or users who prefer to operate directly from the Python source code.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/elijahdsouza-aera/jira-cli.git
    cd jira-cli
    ```
2.  **Install from Source:**
    Ensure Python is installed (verify with `python --version` or `python3 --version`; download from [python.org/downloads](https://www.python.org/downloads/) if necessary).
    Install the package and its dependencies using pip:
    ```bash
    pip install .
    ```
    For active development, install in editable mode:
    ```bash
    pip install -e .
    ```

## Configuration

To establish connectivity with Jira and GitHub, the CLI requires specific credentials, which are securely stored locally on your machine.

1.  **Initiate Configuration:**
    ```bash
    Aera-Jira-CLI config
    ```
    *For source installations, utilize `jira-cli config`.*

2.  **Provide Credentials:**
    The utility will prompt for the following information:
    -   **Jira Server URL**: Your Jira instance's web address (e.g., `https://your-company.atlassian.net`).
    -   **Jira Username**: The email associated with your Jira account.
    -   **Jira API Token**: An API token, obtainable via [Atlassian's guide](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).
    -   **GitHub Repository Owner**: The GitHub organization or username owning the repository (e.g., `elijahdsouza-aera`).
    -   **GitHub Repository Name**: The name of the GitHub repository (e.g., `jira-cli`).
    -   **GitHub Personal Access Token**: A Personal Access Token (PAT) with `repo` scope, generated per [GitHub's documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

## Usage

Upon successful installation and configuration, the Aera Jira AI CLI is ready for use.

**Example: Suggest Jira Actions for a Pull Request**

To obtain AI-driven suggestions for a GitHub pull request (e.g., PR #123):

```bash
Aera-Jira-CLI suggest --pr 123
```
*For source installations, utilize `jira-cli suggest --pr 123`.*

The CLI will analyze the pull request and propose relevant Jira actions, which can then be approved or rejected.

**Additional Usage Examples:**

Suggestions can also be generated for specific commits or branches:

```bash
# Suggestions for a commit
Aera-Jira-CLI suggest --commit <commit_sha>

# Suggestions for a branch
Aera-Jira-CLI suggest --branch <branch_name>
```

---

For inquiries or feedback, please utilize the [GitHub repository's issue tracker](https://github.com/elijahdsouza-aera/jira-cli/issues).