"""Logs viewing commands."""

import click
import time
from suna_ultra import SunaClient
from suna_ultra.exceptions import SunaError
from ..auth import ensure_authenticated
from ..config import config
from ..output import print_error, print_warning


@click.command(name="logs")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--agent-id", "-a", help="Filter by agent ID")
@click.option("--task-id", "-t", help="Filter by task ID")
@click.option("--tail", default=100, help="Number of lines to show from the end")
def logs_command(follow, agent_id, task_id, tail):
    """View and stream logs."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        if not agent_id and not task_id:
            print_error("Please specify either --agent-id or --task-id")
            raise click.Abort()
        
        if follow:
            if task_id:
                # Stream task events
                click.echo(f"Streaming logs for task {task_id}...")
                try:
                    for event in client.tasks.stream(task_id):
                        timestamp = event.timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
                        click.echo(f"[{timestamp}] [{event.event}] {event.data}")
                except KeyboardInterrupt:
                    click.echo("\nStopped following logs.")
            else:
                print_warning("Live streaming for agent logs not yet implemented.")
                print_warning("Use --task-id to stream task-specific logs.")
        else:
            print_warning("Static log viewing not yet implemented.")
            print_warning("Use --follow to stream real-time logs.")
    
    except SunaError as e:
        print_error(f"Failed to view logs: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()
