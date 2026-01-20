import subprocess
import json
import click
import os

class LLMIntegration:
    def __init__(self):
        # Placeholder for potential API key or configuration if Gemini CLI requires it
        pass

    def call_gemini(self, prompt: str) -> dict:
        """
        Calls the Gemini CLI with a given prompt and parses the JSON output.
        Assumes the 'gemini' CLI tool is installed and configured.
        """
        command = ["gemini", "pro", "-o", "json", prompt] # Assuming 'gemini pro -o json' for JSON output
        click.echo(f"Calling Gemini CLI with command: {' '.join(command)}", err=False)

        try:
            # Execute the Gemini CLI command
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the JSON output
            gemini_output = process.stdout.strip()
            click.echo(f"Gemini raw output: {gemini_output}", err=False)

            # The Gemini CLI might return JSON wrapped in markdown, or plain JSON.
            # We need to handle both cases.
            if gemini_output.startswith("```json") and gemini_output.endswith("```"):
                json_string = gemini_output[7:-3].strip()
            else:
                json_string = gemini_output

            parsed_output = json.loads(json_string)
            self._validate_gemini_output(parsed_output)
            return parsed_output

        except FileNotFoundError:
            click.echo("Error: `gemini` command not found. Please ensure it is in your PATH and installed.", err=True)
            return {"actions": []}
        except subprocess.CalledProcessError as e:
            click.echo(f"Error calling Gemini CLI: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}", err=True)
            return {"actions": []}
        except json.JSONDecodeError as e:
            click.echo(f"Error decoding JSON from Gemini CLI output: {e}\nOutput: {gemini_output}", err=True)
            return {"actions": []}
        except ValueError as e:
            click.echo(f"Gemini output validation error: {e}", err=True)
            return {"actions": []}

    def _validate_gemini_output(self, output: dict):
        """
        Validates the structure of the Gemini CLI output against the PRD schema.
        Raises ValueError if the structure is invalid.
        """
        if not isinstance(output, dict) or "actions" not in output:
            raise ValueError("Gemini output must be a dictionary with an 'actions' key.")
        
        if not isinstance(output["actions"], list):
            raise ValueError("The 'actions' key in Gemini output must be a list.")
        
        for action in output["actions"]:
            if not isinstance(action, dict) or "type" not in action:
                raise ValueError("Each action in Gemini output must be a dictionary with a 'type' key.")
            
            # Further validation based on action type could be added here
            # For example:
            # if action["type"] == "create_ticket":
            #    if not all(k in action for k in ["issue_type", "summary", "description", "confidence"]):
            #        raise ValueError("create_ticket action missing required fields.")
            # elif action["type"] == "use_existing_ticket":
            #    if not all(k in action for k in ["issue_key", "similarity", "reason"]):
            #        raise ValueError("use_existing_ticket action missing required fields.")
