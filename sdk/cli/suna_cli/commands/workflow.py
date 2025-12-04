"""Workflow management commands."""

import click
import json
from suna_ultra import SunaClient
from suna_ultra.exceptions import SunaError
from ..auth import ensure_authenticated
from ..config import config
from ..output import (
    print_workflows_table,
    print_json,
    print_error,
    print_success,
    create_spinner,
)


@click.group(name="workflow")
def workflow_group():
    """Manage workflows."""
    pass


@workflow_group.command("list")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_workflows(format):
    """List all workflows."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner("Fetching workflows...") as progress:
            progress.add_task("fetch", total=None)
            workflows = client.workflows.list()
        
        if format == "json":
            print_json([wf.model_dump() for wf in workflows])
        else:
            print_workflows_table(workflows)
    
    except SunaError as e:
        print_error(f"Failed to list workflows: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@workflow_group.command("create")
@click.option("--name", required=True, help="Workflow name")
@click.option("--definition", "-d", required=True, help="Workflow definition (JSON string or file path)")
def create_workflow(name, definition):
    """Create a new workflow."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        # Try to parse as JSON, or read from file
        try:
            workflow_def = json.loads(definition)
        except json.JSONDecodeError:
            # Try reading from file
            try:
                with open(definition, 'r') as f:
                    workflow_def = json.load(f)
            except Exception:
                print_error("Invalid workflow definition. Must be JSON string or file path.")
                raise click.Abort()
        
        with create_spinner(f"Creating workflow '{name}'...") as progress:
            progress.add_task("create", total=None)
            workflow = client.workflows.create(name=name, definition=workflow_def)
        
        print_success(f"Workflow created successfully! ID: {workflow.id}")
        print_json(workflow.model_dump())
    
    except SunaError as e:
        print_error(f"Failed to create workflow: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@workflow_group.command("get")
@click.argument("workflow_id")
def get_workflow(workflow_id):
    """Get workflow details."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Fetching workflow {workflow_id}...") as progress:
            progress.add_task("fetch", total=None)
            workflow = client.workflows.get(workflow_id)
        
        print_json(workflow.model_dump())
    
    except SunaError as e:
        print_error(f"Failed to get workflow: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@workflow_group.command("run")
@click.argument("workflow_id")
@click.option("--inputs", "-i", help="Workflow inputs (JSON string or file path)")
def run_workflow(workflow_id, inputs):
    """Execute a workflow."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        # Parse inputs if provided
        workflow_inputs = None
        if inputs:
            try:
                workflow_inputs = json.loads(inputs)
            except json.JSONDecodeError:
                try:
                    with open(inputs, 'r') as f:
                        workflow_inputs = json.load(f)
                except Exception:
                    print_error("Invalid inputs. Must be JSON string or file path.")
                    raise click.Abort()
        
        with create_spinner(f"Running workflow {workflow_id}...") as progress:
            progress.add_task("run", total=None)
            run = client.workflows.run(workflow_id, inputs=workflow_inputs)
        
        print_success(f"Workflow execution started! Run ID: {run.id}")
        print_json(run.model_dump())
    
    except SunaError as e:
        print_error(f"Failed to run workflow: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()


@workflow_group.command("delete")
@click.argument("workflow_id")
@click.confirmation_option(prompt="Are you sure you want to delete this workflow?")
def delete_workflow(workflow_id):
    """Delete a workflow."""
    try:
        api_key = ensure_authenticated()
        client = SunaClient(api_key=api_key, base_url=config.base_url)
        
        with create_spinner(f"Deleting workflow {workflow_id}...") as progress:
            progress.add_task("delete", total=None)
            client.workflows.delete(workflow_id)
        
        print_success(f"Workflow {workflow_id} deleted successfully!")
    
    except SunaError as e:
        print_error(f"Failed to delete workflow: {e.message}")
        raise click.Abort()
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        raise click.Abort()
