import subprocess
import json
import click
import os
import litellm 
from .config_manager import ConfigManager

class LLMIntegration:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.provider = self.config.get("LLM_PROVIDER", "gemini-cli").lower()
        self.model = self.config.get("LLM_MODEL")
        self.api_key = self.config.get("LLM_API_KEY")
        self.custom_command = self.config.get("LLM_CUSTOM_COMMAND")

        # Set API key for litellm if applicable
        if self.api_key:
            if self.provider == 'openai':
                os.environ["OPENAI_API_KEY"] = self.api_key
            elif self.provider == 'anthropic':
                os.environ["ANTHROPIC_API_KEY"] = self.api_key
            elif self.provider == 'gemini':
                os.environ["GEMINI_API_KEY"] = self.api_key

    def call_llm(self, prompt: str) -> dict:
        """
        Generic entry point to call the configured LLM provider.
        """
        if self.provider == 'gemini-cli':
            return self._call_gemini_cli(prompt)
        elif self.provider == 'custom-cli':
            return self._call_custom_cli(prompt)
        elif self.provider in ['openai', 'anthropic', 'gemini']:
            return self._call_litellm(prompt)
        else:
            click.echo(f"Error: Unsupported LLM provider '{self.provider}'", err=True)
            return {"actions": []}

    def _call_litellm(self, prompt: str) -> dict:
        """
        Calls an LLM via the litellm library.
        """
        model_name = self.model
        # Map provider to litellm model prefix if needed
        if self.provider == 'openai' and not model_name.startswith('openai/'):
            model_name = f"openai/{model_name}"
        elif self.provider == 'anthropic' and not model_name.startswith('anthropic/'):
            model_name = f"anthropic/{model_name}"
        elif self.provider == 'gemini' and not model_name.startswith('gemini/'):
            model_name = f"gemini/{model_name}"

        click.echo(f"Calling LLM ({model_name}) via litellm...", err=False)

        try:
            response = litellm.completion(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"} if self.provider == 'openai' else None
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_and_validate(content)

        except Exception as e:
            click.echo(f"Error calling LLM via litellm: {e}", err=True)
            return {"actions": []}

    def _call_gemini_cli(self, prompt: str) -> dict:
        """
        Calls the Gemini CLI with a given prompt.
        """
        command = ["gemini", "pro", "-o", "json", prompt]
        return self._run_command(command, "Gemini CLI")

    def _call_custom_cli(self, prompt: str) -> dict:
        """
        Calls a user-defined custom CLI command.
        """
        if not self.custom_command:
            click.echo("Error: Custom CLI command not configured.", err=True)
            return {"actions": []}
        
        # Replace {prompt} placeholder or append if not present
        if "{prompt}" in self.custom_command:
            command_str = self.custom_command.replace("{prompt}", prompt)
        else:
            command_str = f"{self.custom_command} \"{prompt}\""
        
        # Using shell=True for custom commands to support pipes/redirects if needed
        # but caution: security implications.
        click.echo(f"Calling Custom CLI with command: {command_str}", err=False)
        
        try:
            process = subprocess.run(
                command_str,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return self._parse_and_validate(process.stdout.strip())
        except Exception as e:
            click.echo(f"Error calling Custom CLI: {e}", err=True)
            return {"actions": []}

    def _run_command(self, command, name):
        click.echo(f"Calling {name} with command: {' '.join(command)}", err=False)
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            return self._parse_and_validate(process.stdout.strip())
        except FileNotFoundError:
            click.echo(f"Error: `{command[0]}` command not found.", err=True)
            return {"actions": []}
        except subprocess.CalledProcessError as e:
            click.echo(f"Error calling {name}: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}", err=True)
            return {"actions": []}

    def _parse_and_validate(self, output: str) -> dict:
        try:
            # Handle potential markdown wrapping
            if output.startswith("```json") and output.endswith("```"):
                json_string = output[7:-3].strip()
            elif output.startswith("```") and output.endswith("```"):
                json_string = output[3:-3].strip()
            else:
                json_string = output

            parsed_output = json.loads(json_string)
            self._validate_output(parsed_output)
            return parsed_output
        except json.JSONDecodeError as e:
            click.echo(f"Error decoding JSON: {e}\nOutput: {output}", err=True)
            return {"actions": []}
        except ValueError as e:
            click.echo(f"Validation error: {e}", err=True)
            return {"actions": []}

    def _validate_output(self, output: dict):
        if not isinstance(output, dict) or "actions" not in output:
            raise ValueError("Output must be a dictionary with an 'actions' key.")
        
        if not isinstance(output["actions"], list):
            raise ValueError("The 'actions' key must be a list.")
        
        for action in output["actions"]:
            if not isinstance(action, dict) or "type" not in action:
                raise ValueError("Each action must be a dictionary with a 'type' key.")
