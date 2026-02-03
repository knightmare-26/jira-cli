import pytest
from click.testing import CliRunner
from importlib.metadata import version
from jira_ai_cli.cli import cli

def test_suggest_with_multiple_options():
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli, ['suggest', '--pr', '123', '--commit', 'abc', '--no-animation'])
    assert result.exit_code != 0
    assert "Error: Please provide only one of --pr, --commit, or --branch." in result.stdout

def test_version_option():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    expected_version = f"cli, version {version('jira-ai-cli')}"
    assert expected_version in result.output
