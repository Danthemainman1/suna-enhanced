# Suna Ultra Python SDK

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Official Python SDK for the Suna Ultra AI Agent Platform.

## 📦 Installation

```bash
pip install suna-ultra
```

Or install from source:

```bash
cd sdk/python
pip install -e .
```

## 🔑 Authentication

Get your API key from [https://suna.so/settings/api-keys](https://suna.so/settings/api-keys)

Set it as an environment variable:

```bash
export SUNA_API_KEY="sk-your-api-key"
```

Or pass it directly to the client:

```python
from suna_ultra import SunaClient

client = SunaClient(api_key="sk-your-api-key")
```

## 🚀 Quick Start

### Synchronous Client

```python
from suna_ultra import SunaClient

# Initialize client
client = SunaClient(api_key="sk-...")

# Create an agent
agent = client.agents.create(
    name="Research Agent",
    type="research",
    system_prompt="You are a helpful research assistant."
)

# Submit a task
task = client.tasks.submit(
    agent.agent_id,
    "Research the latest trends in AI",
    priority=5
)

# Wait for completion
result = client.tasks.wait(task.id, timeout=300)
print(f"Task completed: {result.output}")

# List all agents
agents = client.agents.list()
for agent in agents:
    print(f"Agent: {agent.name} ({agent.agent_id})")
```

### Asynchronous Client

```python
import asyncio
from suna_ultra import AsyncSunaClient

async def main():
    async with AsyncSunaClient(api_key="sk-...") as client:
        # Create agent
        agent = await client.agents.create(
            name="Async Agent",
            type="general"
        )
        
        # Submit task
        task = await client.tasks.submit(
            agent.agent_id,
            "Write a summary of quantum computing"
        )
        
        # Stream events in real-time
        async for event in client.tasks.stream(task.id):
            print(f"Event: {event.event}")
            if event.data:
                print(f"Data: {event.data}")

asyncio.run(main())
```

## 📚 API Reference

### Client

```python
from suna_ultra import SunaClient

client = SunaClient(
    api_key="sk-...",           # Optional if SUNA_API_KEY env var is set
    base_url="http://localhost:8000",  # Default
    timeout=30                   # Request timeout in seconds
)
```

### Agents

```python
# Create agent
agent = client.agents.create(
    name="Agent Name",
    type="research",  # or "coding", "general", etc.
    capabilities=["web_search", "code_execution"],
    config={"temperature": 0.7},
    system_prompt="You are a helpful assistant."
)

# Get agent
agent = client.agents.get(agent_id)

# List agents
agents = client.agents.list(limit=100, offset=0)

# Update agent
agent = client.agents.update(agent_id, name="New Name")

# Delete agent
client.agents.delete(agent_id)

# Pause/Resume agent
client.agents.pause(agent_id)
client.agents.resume(agent_id)
```

### Tasks

```python
# Submit task
task = client.tasks.submit(
    agent_id="agent-123",
    description="Task description",
    priority=5,  # 1-10
    context={"key": "value"}
)

# Get task status
task = client.tasks.get(task_id)

# List tasks
tasks = client.tasks.list(
    agent_id="agent-123",  # Optional filter
    status="running",       # Optional filter
    limit=100
)

# Cancel task
client.tasks.cancel(task_id)

# Wait for task completion
result = client.tasks.wait(
    task_id,
    timeout=300,       # Max wait time in seconds
    poll_interval=2    # Check every 2 seconds
)

# Stream task events
for event in client.tasks.stream(task_id):
    print(event.event, event.data)
```

### Workflows

```python
# Create workflow
workflow = client.workflows.create(
    name="My Workflow",
    definition={
        "steps": [
            {"id": "step1", "agent": "agent-1", "task": "Do X"},
            {"id": "step2", "agent": "agent-2", "task": "Do Y", "depends_on": ["step1"]}
        ]
    }
)

# Get workflow
workflow = client.workflows.get(workflow_id)

# List workflows
workflows = client.workflows.list()

# Update workflow
workflow = client.workflows.update(workflow_id, definition={...})

# Delete workflow
client.workflows.delete(workflow_id)

# Run workflow
run = client.workflows.run(
    workflow_id,
    inputs={"param1": "value1"}
)
```

### Tools

```python
# List all tools
tools = client.tools.list()

# List tools by category
tools = client.tools.list(category="communication")

# Get tool details
tool = client.tools.get("web_search")

# Execute a tool
result = client.tools.execute(
    "web_search",
    query="AI trends 2024",
    max_results=10
)
```

## 🔄 Streaming

The SDK supports real-time streaming of task events using Server-Sent Events (SSE):

```python
# Sync streaming
for event in client.tasks.stream(task_id):
    if event.event == "progress":
        print(f"Progress: {event.data.get('percentage')}%")
    elif event.event == "complete":
        print("Task completed!")

# Async streaming
async for event in client.tasks.stream(task_id):
    print(f"Event: {event.event}")
```

## ⚠️ Error Handling

```python
from suna_ultra import (
    SunaError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    TimeoutError
)

try:
    agent = client.agents.get("non-existent-id")
except NotFoundError as e:
    print(f"Agent not found: {e.message}")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except SunaError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## 🧪 Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest --cov=suna_ultra --cov-report=html tests/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: [https://suna.so](https://suna.so)
- **Documentation**: [https://docs.suna.so](https://docs.suna.so)
- **GitHub**: [https://github.com/kortix-ai/suna](https://github.com/kortix-ai/suna)
- **Support**: [support@suna.so](mailto:support@suna.so)
