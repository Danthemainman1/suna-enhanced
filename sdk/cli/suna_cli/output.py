"""Rich output formatting for Suna CLI."""

from typing import List, Any, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
import json


console = Console()


def print_agents_table(agents: List[Any]):
    """Display agents in a formatted table."""
    if not agents:
        console.print("[yellow]No agents found.[/yellow]")
        return
    
    table = Table(title="Agents", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="blue")
    table.add_column("Status", style="yellow")
    
    for agent in agents:
        agent_id = getattr(agent, 'agent_id', 'N/A')
        name = getattr(agent, 'name', 'N/A')
        agent_type = getattr(agent, 'type', 'N/A')
        status = getattr(agent, 'status', 'N/A')
        table.add_row(agent_id, name, agent_type, status)
    
    console.print(table)


def print_tasks_table(tasks: List[Any]):
    """Display tasks in a formatted table."""
    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return
    
    table = Table(title="Tasks", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Agent ID", style="blue")
    table.add_column("Description", style="white", max_width=50)
    table.add_column("Status", style="yellow")
    table.add_column("Priority", style="green")
    
    for task in tasks:
        task_id = getattr(task, 'id', 'N/A')
        agent_id = getattr(task, 'agent_id', 'N/A')
        description = getattr(task, 'description', 'N/A')
        status = getattr(task, 'status', 'N/A')
        priority = str(getattr(task, 'priority', 'N/A'))
        
        # Truncate long descriptions
        if len(description) > 50:
            description = description[:47] + "..."
        
        table.add_row(task_id, agent_id, description, status, priority)
    
    console.print(table)


def print_workflows_table(workflows: List[Any]):
    """Display workflows in a formatted table."""
    if not workflows:
        console.print("[yellow]No workflows found.[/yellow]")
        return
    
    table = Table(title="Workflows", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    
    for workflow in workflows:
        workflow_id = getattr(workflow, 'id', 'N/A')
        name = getattr(workflow, 'name', 'N/A')
        status = getattr(workflow, 'status', 'N/A')
        table.add_row(workflow_id, name, status)
    
    console.print(table)


def print_tools_table(tools: List[Any]):
    """Display tools in a formatted table."""
    if not tools:
        console.print("[yellow]No tools found.[/yellow]")
        return
    
    table = Table(title="Tools", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="blue")
    table.add_column("Description", style="white", max_width=60)
    
    for tool in tools:
        name = getattr(tool, 'name', 'N/A')
        category = getattr(tool, 'category', 'N/A')
        description = getattr(tool, 'description', 'N/A')
        
        # Truncate long descriptions
        if description and len(description) > 60:
            description = description[:57] + "..."
        
        table.add_row(name, category, description or '')
    
    console.print(table)


def print_task_status(task: Any):
    """Display detailed task status."""
    status_color = {
        "pending": "yellow",
        "running": "blue",
        "completed": "green",
        "failed": "red",
        "cancelled": "orange1"
    }.get(getattr(task, 'status', '').lower(), "white")
    
    content = f"""
[bold]Task ID:[/bold] {getattr(task, 'id', 'N/A')}
[bold]Agent ID:[/bold] {getattr(task, 'agent_id', 'N/A')}
[bold]Description:[/bold] {getattr(task, 'description', 'N/A')}
[bold]Status:[/bold] [{status_color}]{getattr(task, 'status', 'N/A')}[/{status_color}]
[bold]Priority:[/bold] {getattr(task, 'priority', 'N/A')}
[bold]Created:[/bold] {getattr(task, 'created_at', 'N/A')}
    """.strip()
    
    panel = Panel(content, title="Task Status", border_style="cyan")
    console.print(panel)


def print_agent_info(agent: Any):
    """Display detailed agent information."""
    content = f"""
[bold]Agent ID:[/bold] {getattr(agent, 'agent_id', 'N/A')}
[bold]Name:[/bold] {getattr(agent, 'name', 'N/A')}
[bold]Type:[/bold] {getattr(agent, 'type', 'N/A')}
[bold]Status:[/bold] {getattr(agent, 'status', 'N/A')}
[bold]Created:[/bold] {getattr(agent, 'created_at', 'N/A')}
    """.strip()
    
    if hasattr(agent, 'system_prompt') and agent.system_prompt:
        content += f"\n\n[bold]System Prompt:[/bold]\n{agent.system_prompt}"
    
    panel = Panel(content, title="Agent Information", border_style="green")
    console.print(panel)


def print_json(data: Any):
    """Display data as formatted JSON."""
    if hasattr(data, 'model_dump'):
        # Pydantic model
        json_str = json.dumps(data.model_dump(), indent=2)
    elif hasattr(data, 'dict'):
        # Pydantic v1 model
        json_str = json.dumps(data.dict(), indent=2)
    else:
        json_str = json.dumps(data, indent=2, default=str)
    
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(syntax)


def print_error(message: str):
    """Display an error message."""
    console.print(f"[red]✗ Error:[/red] {message}", style="bold")


def print_success(message: str):
    """Display a success message."""
    console.print(f"[green]✓[/green] {message}", style="bold")


def print_warning(message: str):
    """Display a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}", style="bold")


def print_info(message: str):
    """Display an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def create_spinner(text: str) -> Progress:
    """Create a spinner progress indicator."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    )
