"""Tool management commands."""

import click
from suna_ultra import SunaClient
from suna_ultra.exceptions import SunaError
from ..auth import ensure_authenticated
from ..config import config
from ..output import (
    print_tools_table,
    print_json,
    print_error,
    print_success,
    create_spinner,
)


@click.group(name="tool")
def tool_group():
    """Manage and execute tools."""
    pass


@tool_group.command("list")
@click.option("--category", "-c", help="Filter by category")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_tools(category, format):
    """List available tools."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner("Fetching tools...") as progress:
            progress.add_task("fetch", total=None)
            tools = client.tools.list(category=category)
        
        if format == "json":
            print_json([tool.model_dump() for tool in tools])
        else:
            print_tools_table(tools)
    
    except SunaError as e:
        print_error(f"Failed to list tools: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@tool_group.command("info")
@click.argument("tool_name")
def tool_info(tool_name):
    """Get detailed information about a tool."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Fetching tool '{tool_name}'...") as progress:
            progress.add_task("fetch", total=None)
            tool = client.tools.get(tool_name)
        
        print_json(tool.model_dump())
    
    except SunaError as e:
        print_error(f"Failed to get tool info: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()
