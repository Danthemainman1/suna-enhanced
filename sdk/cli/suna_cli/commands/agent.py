"""Agent management commands."""

import click
from suna_ultra import SunaClient
from suna_ultra.exceptions import SunaError
from ..auth import ensure_authenticated
from ..config import config
from ..output import (
    print_agents_table,
    print_agent_info,
    print_json,
    print_error,
    print_success,
    print_task_status,
    create_spinner,
)


@click.group(name="agent")
def agent_group():
    """Manage agents."""
    pass


@agent_group.command("list")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.option("--limit", default=100, help="Maximum number of agents to list")
def list_agents(format, limit):
    """List all agents."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner("Fetching agents...") as progress:
            progress.add_task("fetch", total=None)
            agents = client.agents.list(limit=limit)
        
        if format == "json":
            print_json([agent.model_dump() for agent in agents])
        else:
            print_agents_table(agents)
    
    except SunaError as e:
        print_error(f"Failed to list agents: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@agent_group.command("create")
@click.option("--name", required=True, help="Agent name")
@click.option("--type", required=True, help="Agent type (e.g., research, coding, general)")
@click.option("--capability", "-c", multiple=True, help="Agent capabilities")
@click.option("--system-prompt", help="System prompt for the agent")
def create_agent(name, type, capability, system_prompt):
    """Create a new agent."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        capabilities = list(capability) if capability else None
        
        with create_spinner(f"Creating agent '{name}'...") as progress:
            progress.add_task("create", total=None)
            agent = client.agents.create(
                name=name,
                type=type,
                capabilities=capabilities,
                system_prompt=system_prompt
            )
        
        print_success(f"Agent created successfully! ID: {agent.agent_id}")
        print_agent_info(agent)
    
    except SunaError as e:
        print_error(f"Failed to create agent: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@agent_group.command("get")
@click.argument("agent_id")
@click.option("--format", type=click.Choice(["info", "json"]), default="info", help="Output format")
def get_agent(agent_id, format):
    """Get agent details."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Fetching agent {agent_id}...") as progress:
            progress.add_task("fetch", total=None)
            agent = client.agents.get(agent_id)
        
        if format == "json":
            print_json(agent.model_dump())
        else:
            print_agent_info(agent)
    
    except SunaError as e:
        print_error(f"Failed to get agent: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@agent_group.command("delete")
@click.argument("agent_id")
@click.confirmation_option(prompt="Are you sure you want to delete this agent?")
def delete_agent(agent_id):
    """Delete an agent."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Deleting agent {agent_id}...") as progress:
            progress.add_task("delete", total=None)
            client.agents.delete(agent_id)
        
        print_success(f"Agent {agent_id} deleted successfully!")
    
    except SunaError as e:
        print_error(f"Failed to delete agent: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@agent_group.command("run")
@click.argument("agent_id")
@click.argument("description")
@click.option("--wait/--no-wait", default=True, help="Wait for task completion")
@click.option("--stream/--no-stream", default=False, help="Stream task events")
@click.option("--priority", default=5, type=int, help="Task priority (1-10)")
def run_agent(agent_id, description, wait, stream, priority):
    """Run a task on an agent."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        # Submit task
        with create_spinner("Submitting task...") as progress:
            progress.add_task("submit", total=None)
            task = client.tasks.submit(agent_id, description, priority=priority)
        
        print_success(f"Task submitted! ID: {task.id}")
        
        if stream:
            # Stream events
            click.echo("\nStreaming events...")
            try:
                for event in client.tasks.stream(task.id):
                    click.echo(f"[{event.event}] {event.data}")
            except KeyboardInterrupt:
                click.echo("\nStreaming interrupted.")
        
        elif wait:
            # Wait for completion
            with create_spinner("Waiting for task completion...") as progress:
                progress.add_task("wait", total=None)
                result = client.tasks.wait(task.id, timeout=300)
            
            print_success("Task completed!")
            if result.output:
                click.echo(f"\n{result.output}")
        else:
            print_task_status(task)
    
    except SunaError as e:
        print_error(f"Failed to run task: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@agent_group.command("pause")
@click.argument("agent_id")
def pause_agent(agent_id):
    """Pause an agent."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Pausing agent {agent_id}...") as progress:
            progress.add_task("pause", total=None)
            agent = client.agents.pause(agent_id)
        
        print_success(f"Agent {agent_id} paused successfully!")
        print_agent_info(agent)
    
    except SunaError as e:
        print_error(f"Failed to pause agent: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@agent_group.command("resume")
@click.argument("agent_id")
def resume_agent(agent_id):
    """Resume a paused agent."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Resuming agent {agent_id}...") as progress:
            progress.add_task("resume", total=None)
            agent = client.agents.resume(agent_id)
        
        print_success(f"Agent {agent_id} resumed successfully!")
        print_agent_info(agent)
    
    except SunaError as e:
        print_error(f"Failed to resume agent: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()
