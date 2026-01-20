# LLM-Assisted Jira CLI

This CLI tool helps developers interact with Jira directly from the command line, using an LLM (like Gemini) to assist with reasoning and ticket creation.

## Prerequisites

- Python 3.7+ (for local development)
- `pip` and `git` (for local development)
- Docker (for containerized usage)

## Installation

### A. Local Installation (for development or non-containerized use)

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd jira-ai-cli
    ```

2.  **Install the CLI:**

    Install the package using `pip`. This command will also install all the required dependencies (`click`, `requests`, `jira`, `PyYAML`, `halo`, etc.) and make the `jira-cli` command available in your terminal.

    ```bash
    pip install .
    ```

    *Note: If you are actively developing the CLI, you can install it in "editable" mode with `pip install -e .`. This allows your changes to the source code to be immediately reflected when you run the `jira-cli` command.*

### B. Docker Installation (Recommended for easy and reproducible usage)

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd jira-ai-cli
    ```

2.  **Build the Docker image:**

    ```bash
    docker build -t jira-cli .
    ```

3.  **Create an alias for easy usage:**

    To use `jira-cli` as a native command, add the following alias to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`, `~/.profile`):

    ```bash
    alias jira-cli='docker run --rm -it \
      -v ~/.jira-cli:/config \
      -v "$(pwd)":/work \
      -e JIRA_SERVER \
      -e JIRA_USERNAME \
      -e JIRA_API_TOKEN \
      -e GITHUB_TOKEN \
      -e GITHUB_OWNER \
      -e GITHUB_REPO \
      -e CI \
      jira-cli'
    ```
    After adding the alias, reload your shell configuration (e.g., `source ~/.zshrc`).

    *Note: For the alias to work, you must ensure that your Jira and GitHub environment variables are set in your shell session or through your `config.json` file.*

## Configuration

After installation (either local or Docker), you need to configure the CLI with your Jira and GitHub credentials. The CLI includes an interactive command to guide you through this setup.

1.  **Run the `config` command:**

    ```bash
    jira-cli config
    ```

2.  **Provide your credentials:**

    The tool will prompt you for the following information:
    - Your Jira Server URL (e.g., `https://your-domain.atlassian.net`)
    - Your Jira Username (the email you use to log in)
    - Your Jira API Token (this can be generated from your Atlassian account settings)
    - Your GitHub Repository Owner (the organization or username that owns the repo)
    - Your GitHub Repository Name
    - Your GitHub Personal Access Token (with `repo` scope)

    Your credentials will be stored securely locally in `~/.jira-cli/config.json`. This file will be automatically mounted into the Docker container via the alias.

## Usage

Once the CLI is installed and configured, you can start using it.

**Example: Suggest Jira actions for a Pull Request**

```bash
jira-cli suggest --pr 123
```

**Animation Control**

The CLI features tasteful animations and spinners to enhance the user experience.

-   **Disable Animation Flag:** You can disable animations for a single run using the `--no-animation` flag:
    ```bash
jira-cli suggest --pr 123 --no-animation
    ```
-   **CI Auto-Disable:** Animations are automatically disabled if the `CI` environment variable is set to `true` (e.g., in continuous integration environments).