import os
import json
import click

CONFIG_DIR = os.path.expanduser("~/.jira-ai-cli")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class ConfigManager:
    def __init__(self, config_file_path=None):
        self._config_file_path = config_file_path if config_file_path else CONFIG_FILE
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensures that the configuration directory exists."""
        # Use the directory of the config file path
        config_dir = os.path.dirname(self._config_file_path) if self._config_file_path != CONFIG_FILE else CONFIG_DIR
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
                click.echo(f"Created configuration directory at {config_dir}", err=False)
            except OSError as e:
                click.echo(f"Error creating configuration directory at {config_dir}: {e}", err=True)

    def save_config(self, config_data):
        """Saves configuration data to the config file."""
        try:
            with open(self._config_file_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            click.echo(click.style(f"Configuration saved to {self._config_file_path}", fg='green'))
            return True
        except IOError as e:
            click.echo(f"Error writing to configuration file {self._config_file_path}: {e}", err=True)
            return False

    def load_config(self):
        """Loads configuration data from the config file."""
        if not os.path.exists(self._config_file_path):
            return {} # Return empty config if file doesn't exist
        
        try:
            with open(self._config_file_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            click.echo(f"Error reading or parsing configuration file {self._config_file_path}: {e}", err=True)
            return {}

    def get_value(self, key):
        """Retrieves a specific value from the configuration."""
        config = self.load_config()
        return config.get(key)
