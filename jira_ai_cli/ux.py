import os
import click
from halo import Halo

# Simple ASCII art for the banner
JIRA_CLI_BANNER = r"""
     ____.__                   _________ .__  .__ 
    |    |__|___________       \_   ___ \|  | |__|
    |    |  \_  __ \__  \      /    \  \/|  | |  |
/\__|    |  ||  | \// __ \_    \     \___|  |_|  |
\________|__||__|  (____  /     \______  /____/__|
                        \/             \/         
"""

class AnimationManager:
    def __init__(self, no_animation: bool = False):
        """
        Manages CLI animations (banner and spinners).
        Animations are disabled if `no_animation` is True or if `CI=true` is set.
        """
        self.animation_enabled = not no_animation and os.environ.get("CI") != "true"
        if self.animation_enabled:
            self.spinner = Halo(spinner='dots')

    def show_banner(self):
        """Displays the ASCII art banner if animations are enabled."""
        if self.animation_enabled:
            click.echo(click.style(JIRA_CLI_BANNER, fg='cyan'), nl=False)
            click.echo(click.style("LLM-Assisted CLI\n", fg='blue'))

    def start(self, text: str):
        """Starts the spinner with the given text."""
        if self.animation_enabled:
            self.spinner.start(text)

    def succeed(self, text: str = None):
        """Stops the spinner with a success message."""
        if self.animation_enabled:
            self.spinner.succeed(text)

    def fail(self, text: str = None):
        """Stops the spinner with a failure message."""
        if self.animation_enabled:
            self.spinner.fail(text)
        else:
            click.echo(text)

    def stop(self):
        """Stops the spinner without a message."""
        if self.animation_enabled:
            self.spinner.stop()
