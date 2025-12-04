"""Tests for CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from suna_cli.main import cli
from suna_cli.config import Config


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config(tmp_path):
    """Create a temporary config for testing."""
    config = Config()
    config.config_file = tmp_path / "test_config.json"
    return config


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Suna Ultra" in result.output


def test_cli_version(runner):
    """Test CLI version command."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_status_not_authenticated(runner):
    """Test status command when not authenticated."""
    with patch("suna_cli.main.get_api_key", return_value=None):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "Not authenticated" in result.output


def test_status_authenticated(runner):
    """Test status command when authenticated."""
    with patch("suna_cli.main.get_api_key", return_value="sk-test-key-123"):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "Authenticated" in result.output


def test_agent_list_not_authenticated(runner):
    """Test agent list without authentication."""
    with patch("suna_cli.commands.agent.ensure_authenticated") as mock_auth:
        mock_auth.side_effect = Exception("Authentication required")
        result = runner.invoke(cli, ["agent", "list"])
        assert result.exit_code != 0


def test_config_set(runner, tmp_path):
    """Test config set command."""
    with patch("suna_cli.commands.config_cmd.config") as mock_config:
        result = runner.invoke(cli, ["config", "set", "test_key", "test_value"])
        assert result.exit_code == 0
        assert "updated" in result.output.lower()


def test_config_get(runner):
    """Test config get command."""
    with patch("suna_cli.commands.config_cmd.config") as mock_config:
        mock_config.get.return_value = "test_value"
        result = runner.invoke(cli, ["config", "get", "test_key"])
        assert result.exit_code == 0
        assert "test_value" in result.output


def test_config_get_nonexistent(runner):
    """Test config get for non-existent key."""
    with patch("suna_cli.commands.config_cmd.config") as mock_config:
        mock_config.get.return_value = None
        result = runner.invoke(cli, ["config", "get", "nonexistent_key"])
        assert result.exit_code == 0
        assert "not set" in result.output.lower()


def test_task_group_help(runner):
    """Test task group help."""
    result = runner.invoke(cli, ["task", "--help"])
    assert result.exit_code == 0
    assert "Manage tasks" in result.output


def test_agent_group_help(runner):
    """Test agent group help."""
    result = runner.invoke(cli, ["agent", "--help"])
    assert result.exit_code == 0
    assert "Manage agents" in result.output


def test_workflow_group_help(runner):
    """Test workflow group help."""
    result = runner.invoke(cli, ["workflow", "--help"])
    assert result.exit_code == 0
    assert "Manage workflows" in result.output


def test_tool_group_help(runner):
    """Test tool group help."""
    result = runner.invoke(cli, ["tool", "--help"])
    assert result.exit_code == 0
    assert "tools" in result.output.lower()
