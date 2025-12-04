# Getting Started with Suna Ultra SDK & CLI

This guide will help you get started with both the Python SDK and CLI tool for Suna Ultra.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- A Suna Ultra account and API key

## Installation

### Option 1: Install Both Packages

```bash
# Install SDK
pip install ./sdk/python

# Install CLI
pip install ./sdk/cli
```

### Option 2: Install from PyPI (when published)

```bash
pip install suna-ultra suna-cli
```

## Getting Your API Key

1. Go to [https://suna.so/settings/api-keys](https://suna.so/settings/api-keys)
2. Create a new API key
3. Copy the key (it starts with `sk-`)

## Quick Start with CLI

### 1. Login

```bash
suna login
# Enter your API key when prompted
```

### 2. Check Status

```bash
suna status
```

### 3. Create an Agent

```bash
suna agent create \
  --name "My First Agent" \
  --type research \
  --system-prompt "You are a helpful research assistant."
```

### 4. List Agents

```bash
suna agent list
```

### 5. Run a Task

```bash
# Replace <agent-id> with your agent's ID
suna agent run <agent-id> "Research the latest AI trends" --wait
```

## Quick Start with Python SDK

### 1. Basic Usage

```python
from suna_ultra import SunaClient

# Initialize client (uses SUNA_API_KEY env var or pass directly)
client = SunaClient(api_key="sk-your-key")

# Create an agent
agent = client.agents.create(
    name="Research Agent",
    type="research",
    system_prompt="You are a helpful research assistant."
)

print(f"Created agent: {agent.agent_id}")

# Submit a task
task = client.tasks.submit(
    agent.agent_id,
    "Research AI trends in 2024",
    priority=5
)

print(f"Task submitted: {task.id}")

# Wait for completion
result = client.tasks.wait(task.id, timeout=300)
print(f"Result: {result.output}")

# Close the client
client.close()
```

### 2. Using Context Manager

```python
from suna_ultra import SunaClient

with SunaClient(api_key="sk-your-key") as client:
    agents = client.agents.list()
    for agent in agents:
        print(f"- {agent.name} ({agent.agent_id})")
```

### 3. Async Usage

```python
import asyncio
from suna_ultra import AsyncSunaClient

async def main():
    async with AsyncSunaClient(api_key="sk-your-key") as client:
        # Create agent
        agent = await client.agents.create(
            name="Async Agent",
            type="research"
        )
        
        # Submit task
        task = await client.tasks.submit(
            agent.agent_id,
            "Research topic"
        )
        
        # Stream events
        async for event in client.tasks.stream(task.id):
            print(f"Event: {event.event}")

asyncio.run(main())
```

### 4. Using Environment Variables

```bash
export SUNA_API_KEY="sk-your-key"
export SUNA_BASE_URL="https://api.suna.so"
```

```python
from suna_ultra import SunaClient

# API key is loaded from SUNA_API_KEY automatically
client = SunaClient()
```

## Common CLI Commands

### Configuration

```bash
# Set configuration
suna config set base_url https://api.suna.so

# View configuration
suna config list

# Get specific value
suna config get base_url
```

### Agent Management

```bash
# List agents
suna agent list
suna agent list --format json

# Get agent details
suna agent get <agent-id>

# Delete agent
suna agent delete <agent-id>

# Pause/Resume agent
suna agent pause <agent-id>
suna agent resume <agent-id>
```

### Task Management

```bash
# Submit task
suna task submit --agent <agent-id> "Task description" --priority 8

# Check status
suna task status <task-id>

# List tasks
suna task list
suna task list --status running
suna task list --agent <agent-id>

# Cancel task
suna task cancel <task-id>
```

### Workflow Management

```bash
# List workflows
suna workflow list

# Create workflow from JSON file
suna workflow create --name "My Workflow" --definition workflow.json

# Run workflow
suna workflow run <workflow-id> --inputs '{"param": "value"}'
```

### Tools

```bash
# List all tools
suna tool list

# List by category
suna tool list --category search

# Get tool details
suna tool info web_search
```

### Streaming Logs

```bash
# Stream task logs
suna logs --follow --task-id <task-id>
```

## Common SDK Patterns

### Error Handling

```python
from suna_ultra import SunaClient
from suna_ultra.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    TimeoutError
)

client = SunaClient()

try:
    agent = client.agents.get("agent-123")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Agent not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except TimeoutError:
    print("Request timed out")
```

### Streaming Task Events

```python
from suna_ultra import SunaClient

client = SunaClient()

# Submit task
task = client.tasks.submit("agent-123", "Research topic")

# Stream events
for event in client.tasks.stream(task.id):
    if event.event == "progress":
        print(f"Progress: {event.data.get('percentage')}%")
    elif event.event == "complete":
        print("Task completed!")
        break
```

### Listing with Filters

```python
# List agents
agents = client.agents.list(limit=10, offset=0)

# List tasks by status
running_tasks = client.tasks.list(status="running")

# List tasks by agent
agent_tasks = client.tasks.list(agent_id="agent-123")

# List tools by category
search_tools = client.tools.list(category="search")
```

### Creating Workflows

```python
workflow_definition = {
    "steps": [
        {
            "id": "step1",
            "agent": "agent-1",
            "task": "Research topic"
        },
        {
            "id": "step2",
            "agent": "agent-2",
            "task": "Summarize findings",
            "depends_on": ["step1"]
        }
    ]
}

workflow = client.workflows.create(
    name="Research Pipeline",
    definition=workflow_definition
)

# Run workflow
run = client.workflows.run(workflow.id, inputs={"topic": "AI"})
```

## Tips & Best Practices

### SDK

1. **Use Context Managers**: Always use `with` statements to ensure proper resource cleanup
2. **Handle Errors**: Always wrap API calls in try-except blocks
3. **Environment Variables**: Store API keys in environment variables, not in code
4. **Async for I/O**: Use async client for applications with multiple concurrent operations
5. **Timeouts**: Set appropriate timeouts for long-running operations

### CLI

1. **JSON Output**: Use `--format json` for scripting and automation
2. **Configuration**: Set up your config once with `suna config set`
3. **Filters**: Use filters to narrow down results (e.g., `--status running`)
4. **Streaming**: Use `--stream` or `--follow` for real-time updates
5. **Help**: Use `--help` on any command to see all options

## Troubleshooting

### Authentication Issues

```bash
# Check status
suna status

# Re-login if needed
suna logout
suna login
```

### Connection Issues

```bash
# Check base URL
suna config get base_url

# Update if needed
suna config set base_url https://api.suna.so
```

### Python Import Errors

```bash
# Ensure packages are installed
pip install suna-ultra suna-cli

# Check installation
python -c "import suna_ultra; print(suna_ultra.__version__)"
```

## Next Steps

- Read the full SDK documentation: [sdk/python/README.md](python/README.md)
- Read the full CLI documentation: [sdk/cli/README.md](cli/README.md)
- Check out examples: [sdk/python/example_usage.py](python/example_usage.py)
- View implementation details: [PHASE5_IMPLEMENTATION_SUMMARY.md](../PHASE5_IMPLEMENTATION_SUMMARY.md)

## Support

- **Documentation**: [https://docs.suna.so](https://docs.suna.so)
- **GitHub**: [https://github.com/kortix-ai/suna](https://github.com/kortix-ai/suna)
- **Email**: support@suna.so

## License

Both the SDK and CLI are licensed under the MIT License.
