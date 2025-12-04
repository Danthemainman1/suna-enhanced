"""Task management commands."""

import click
from suna_ultra import SunaClient
from suna_ultra.exceptions import SunaError
from ..auth import ensure_authenticated
from ..config import config
from ..output import (
    print_tasks_table,
    print_task_status,
    print_json,
    print_error,
    print_success,
    create_spinner,
)


@click.group(name="task")
def task_group():
    """Manage tasks."""
    pass


@task_group.command("submit")
@click.option("--agent", "-a", "agent_id", required=True, help="Agent ID")
@click.argument("description")
@click.option("--priority", default=5, type=int, help="Task priority (1-10)")
@click.option("--wait/--no-wait", default=False, help="Wait for completion")
def submit_task(agent_id, description, priority, wait):
    """Submit a new task."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner("Submitting task...") as progress:
            progress.add_task("submit", total=None)
            task = client.tasks.submit(agent_id, description, priority=priority)
        
        print_success(f"Task submitted! ID: {task.id}")
        print_task_status(task)
        
        if wait:
            with create_spinner("Waiting for task completion...") as progress:
                progress.add_task("wait", total=None)
                result = client.tasks.wait(task.id, timeout=300)
            
            print_success("Task completed!")
            if result.output:
                click.echo(f"\n{result.output}")
    
    except SunaError as e:
        print_error(f"Failed to submit task: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@task_group.command("status")
@click.argument("task_id")
@click.option("--format", type=click.Choice(["info", "json"]), default="info", help="Output format")
def task_status(task_id, format):
    """Get task status."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Fetching task {task_id}...") as progress:
            progress.add_task("fetch", total=None)
            task = client.tasks.get(task_id)
        
        if format == "json":
            print_json(task.model_dump())
        else:
            print_task_status(task)
    
    except SunaError as e:
        print_error(f"Failed to get task status: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@task_group.command("cancel")
@click.argument("task_id")
@click.confirmation_option(prompt="Are you sure you want to cancel this task?")
def cancel_task(task_id):
    """Cancel a task."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Cancelling task {task_id}...") as progress:
            progress.add_task("cancel", total=None)
            client.tasks.cancel(task_id)
        
        print_success(f"Task {task_id} cancelled successfully!")
    
    except SunaError as e:
        print_error(f"Failed to cancel task: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@task_group.command("list")
@click.option("--agent", "-a", "agent_id", help="Filter by agent ID")
@click.option("--status", "-s", help="Filter by status")
@click.option("--limit", default=100, help="Maximum number of tasks to list")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_tasks(agent_id, status, limit, format):
    """List tasks."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner("Fetching tasks...") as progress:
            progress.add_task("fetch", total=None)
            tasks = client.tasks.list(agent_id=agent_id, status=status, limit=limit)
        
        if format == "json":
            print_json([task.model_dump() for task in tasks])
        else:
            print_tasks_table(tasks)
    
    except SunaError as e:
        print_error(f"Failed to list tasks: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()
