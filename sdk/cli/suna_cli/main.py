"""Main CLI entry point for Suna."""

import click
from rich.console import Console
from .commands import (
    agent_group,
    task_group,
    workflow_group,
    tool_group,
    logs_command,
    config_group,
)
from .auth import login, logout, get_api_key
from .output import print_success, print_error
from .config import config


console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx):
    """
    Suna Ultra - Autonomous AI Agent Platform
    
    Manage agents, tasks, workflows, and tools from the command line.
    
    Get started:
        1. Run 'suna login' to authenticate
        2. Create an agent with 'suna agent create'
        3. Run tasks with 'suna agent run'
    
    For more help on a command, run: suna COMMAND --help
    """
    ctx.ensure_object(dict)
    ctx.obj["console"] = console
    ctx.obj["config"] = config


@cli.command()
@click.option("--api-key", prompt="Enter your API key", hide_input=True, help="Suna API key")
@click.option("--base-url", default="http://localhost:8000", help="API base URL")
def login_command(api_key, base_url):
    """
    Login to Suna Ultra.
    
    Get your API key from: https://suna.so/settings/api-keys
    """
    try:
        login(api_key)
        
        # Save base URL if different from default
        if base_url != "http://localhost:8000":
            config.set("base_url", base_url)
            print_success(f"Base URL set to: {base_url}")
    
    except Exception as e:
        print_error(f"Login failed: {str(e)}")
        raise click.Abort()


@cli.command()
def logout_command():
    """Logout from Suna Ultra."""
    try:
        api_key = get_api_key()
        if not api_key:
            print_error("Not currently logged in.")
            return
        
        logout()
    
    except Exception as e:
        print_error(f"Logout failed: {str(e)}")
        raise click.Abort()


@cli.command()
def status():
    """Show authentication and configuration status."""
    api_key = get_api_key()
    base_url = config.base_url
    
    console.print("\n[bold]Suna CLI Status[/bold]\n")
    
    if api_key:
        masked_key = f"{api_key[:8]}..." if len(api_key) > 8 else "***"
        console.print(f"[green]✓[/green] Authenticated: {masked_key}")
    else:
        console.print("[red]✗[/red] Not authenticated")
    
    console.print(f"[blue]ℹ[/blue] Base URL: {base_url}")
    
    workspace = config.default_workspace
    if workspace:
        console.print(f"[blue]ℹ[/blue] Default workspace: {workspace}")
    
    console.print()


# Add command groups
cli.add_command(agent_group)
cli.add_command(task_group)
cli.add_command(workflow_group)
cli.add_command(tool_group)
cli.add_command(logs_command)
cli.add_command(config_group)


# Alias for login/logout
cli.add_command(login_command, name="login")
cli.add_command(logout_command, name="logout")


if __name__ == "__main__":
    cli()
