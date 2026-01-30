#!/bin/bash
set -e

# Set the HOME directory to our mounted config volume.
# This ensures that the CLI's config file (stored in ~/.jira-ai-cli)
# is persisted outside the container.
export HOME=/config

# Execute the jira-ai command with all the arguments passed to the script.
# The `exec` command replaces the shell process with the Python process,
# ensuring that signals are handled correctly.
exec jira-cli "$@"
