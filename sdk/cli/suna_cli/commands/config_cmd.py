"""Configuration management commands."""

import click
from ..config import config
from ..output import print_error, print_success, print_info, console
from rich.table import Table


@click.group(name="config")
def config_group():
    """Manage CLI configuration."""
    pass


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """Set a configuration value."""
    try:
        config.set(key, value)
        print_success(f"Configuration updated: {key} = {value}")
    except Exception as e:
        print_error(f"Failed to set configuration: {str(e)}")
        raise click.Abort()


@config_group.command("get")
@click.argument("key")
def get_config(key):
    """Get a configuration value."""
    try:
        value = config.get(key)
        if value is None:
            print_info(f"Configuration key '{key}' not set.")
        else:
            # Mask sensitive values
            if key in ["api_key", "token", "secret"]:
                value = f"{value[:8]}..." if len(value) > 8 else "***"
            click.echo(f"{key}: {value}")
    except Exception as e:
        print_error(f"Failed to get configuration: {str(e)}")
        raise click.Abort()


@config_group.command("list")
def list_config():
    """List all configuration values."""
    try:
        all_config = config.all()
        
        if not all_config:
            print_info("No configuration values set.")
            return
        
        table = Table(title="Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in all_config.items():
            # Mask sensitive values
            if key in ["api_key", "token", "secret"]:
                display_value = f"{value[:8]}..." if len(str(value)) > 8 else "***"
            else:
                display_value = str(value)
            table.add_row(key, display_value)
        
        console.print(table)
    
    except Exception as e:
        print_error(f"Failed to list configuration: {str(e)}")
        raise click.Abort()


@config_group.command("delete")
@click.argument("key")
@click.confirmation_option(prompt="Are you sure you want to delete this configuration key?")
def delete_config(key):
    """Delete a configuration value."""
    try:
        config.delete(key)
        print_success(f"Configuration key '{key}' deleted.")
    except Exception as e:
        print_error(f"Failed to delete configuration: {str(e)}")
        raise click.Abort()


@config_group.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear all configuration?")
def clear_config():
    """Clear all configuration."""
    try:
        config.clear()
        print_success("All configuration cleared.")
    except Exception as e:
        print_error(f"Failed to clear configuration: {str(e)}")
        raise click.Abort()
