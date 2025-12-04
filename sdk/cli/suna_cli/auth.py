"""Authentication helpers for Suna CLI."""

import click
from rich.console import Console
from .config import config


console = Console()


def ensure_authenticated() -> str:
    """
    Ensure user is authenticated and return API key.
    
    Returns:
        API key
    
    Raises:
        click.ClickException: If not authenticated
    """
    api_key = config.api_key
    
    if not api_key:
        console.print(
            "[red]✗[/red] Not authenticated. Please run [cyan]suna login[/cyan] first.",
            style="bold"
        )
        raise click.ClickException("Authentication required")
    
    return api_key


def login(api_key: str):
    """
    Save API key to config.
    
    Args:
        api_key: API key to save
    """
    config.set("api_key", api_key)
    console.print("[green]✓[/green] Successfully logged in!", style="bold")


def logout():
    """Remove API key from config."""
    config.delete("api_key")
    console.print("[green]✓[/green] Successfully logged out!", style="bold")


def get_api_key() -> str | None:
    """Get current API key."""
    return config.api_key
