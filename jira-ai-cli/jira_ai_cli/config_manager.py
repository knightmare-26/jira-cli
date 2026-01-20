import os
import json
import click

CONFIG_DIR = os.path.expanduser("~/.jira-ai-cli")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class ConfigManager:
    def __init__(self):
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensures that the configuration directory exists."""
        if not os.path.exists(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR)
                click.echo(f"Created configuration directory at {CONFIG_DIR}", err=False)
            except OSError as e:
                click.echo(f"Error creating configuration directory at {CONFIG_DIR}: {e}", err=True)

    def save_config(self, config_data):
        """Saves configuration data to the config file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
            click.echo(f"Configuration saved to {CONFIG_FILE}", fg='green')
            return True
        except IOError as e:
            click.echo(f"Error writing to configuration file {CONFIG_FILE}: {e}", err=True)
            return False

    def load_config(self):
        """Loads configuration data from the config file."""
        if not os.path.exists(CONFIG_FILE):
            return {} # Return empty config if file doesn't exist
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            click.echo(f"Error reading or parsing configuration file {CONFIG_FILE}: {e}", err=True)
            return {}

    def get_value(self, key):
        """Retrieves a specific value from the configuration."""
        config = self.load_config()
        return config.get(key)
