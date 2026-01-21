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

The `jira-cli` is designed to be run as a Docker container.

1.  **Pull the Docker Image:**

    The easiest way to use the CLI is to pull the pre-built Docker image from a container registry.
    *(Replace `your-registry/your-username` with your actual registry path, e.g., `ghcr.io/yourusername` or `yourdockerhubusername`)*

    ```bash
    docker pull your-registry/your-username/jira-cli:latest
    ```
    *(If you've built the image locally, use `jira-cli:latest` instead of pulling.)*

2.  **Create an alias for easy usage:**

    To use `jira-cli` like a native command, add the following alias to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`, `~/.profile`):

    ```bash
    alias jira-cli='docker run --rm -it \
      -v ~/.jira-cli:/config \
      -v "$(pwd)":/work \
      -e CI \
      your-registry/your-username/jira-cli:latest'
    ```
    After adding the alias, reload your shell configuration (e.g., `source ~/.zshrc`).

    *   `-v ~/.jira-cli:/config`: This mounts your local `~/.jira-cli` directory into the container, ensuring your configuration persists across runs.
    *   `-v "$(pwd)":/work`: This mounts your current working directory into the container, allowing the CLI to access local files if needed.
    *   `-e CI`: This environment variable is used to automatically disable animations in CI/CD environments.
    *   `your-registry/your-username/jira-cli:latest`: The name of the Docker image.

## Configuration

Before using the CLI, you need to configure it with your Jira and GitHub credentials. The CLI includes an interactive command (`config`) to guide you through this setup. This configuration will be saved persistently in `~/.jira-cli/config.json` on your local machine, thanks to the mounted Docker volume.

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

    Your credentials will be stored securely locally in `~/.jira-cli/config.json`.

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

## Sharing Your Docker Image

To enable others to `docker pull` your image directly, you need to push it to a container registry (e.g., Docker Hub, GitHub Container Registry).

1.  **Build Your Image (if you haven't already):**
    ```bash
    docker build -t jira-cli .
    ```
2.  **Tag Your Image:**
    Tag your local image with the registry, your username, and a repository name.
    *(Replace `your-registry/your-username` with your actual registry path)*
    ```bash
    docker tag jira-cli your-registry/your-username/jira-cli:latest
    # Example for Docker Hub: docker tag jira-cli mydockerhubusername/jira-cli:latest
    # Example for GitHub CR: docker tag jira-cli ghcr.io/mygithubusername/jira-cli:latest
    ```
3.  **Log in to the Registry:**
    ```bash
    docker login your-registry # e.g., docker login ghcr.io
    ```
    (You'll be prompted for credentials.)
4.  **Push the Image:**
    ```bash
    docker push your-registry/your-username/jira-cli:latest
    ```
    Now, others can use the `docker pull` command from the "Docker Installation" section with your published image name.