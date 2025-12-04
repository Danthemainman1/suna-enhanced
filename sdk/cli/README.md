# Suna CLI

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../python/LICENSE)

Command-line interface for the Suna Ultra AI Agent Platform.

## 📦 Installation

```bash
pip install suna-cli
```

Or install from source:

```bash
cd sdk/cli
pip install -e .
```

## 🔑 Authentication

Get your API key from [https://suna.so/settings/api-keys](https://suna.so/settings/api-keys)

Login with your API key:

```bash
suna login
# Enter your API key when prompted
```

Check authentication status:

```bash
suna status
```

## 🚀 Quick Start

```bash
# Login
suna login

# Create an agent
suna agent create --name "Research Agent" --type research

# List agents
suna agent list

# Run a task
suna agent run <agent-id> "Research AI trends"

# List tasks
suna task list

# Check task status
suna task status <task-id>
```

## 📚 Commands Reference

### Authentication

```bash
# Login
suna login

# Logout
suna logout

# Check status
suna status
```

### Agent Management

```bash
# List agents
suna agent list [--format table|json] [--limit N]

# Create agent
suna agent create --name NAME --type TYPE [--capability CAP] [--system-prompt PROMPT]

# Get agent details
suna agent get <agent-id> [--format info|json]

# Delete agent
suna agent delete <agent-id>

# Run task on agent
suna agent run <agent-id> "task description" [--wait] [--stream] [--priority N]

# Pause/Resume agent
suna agent pause <agent-id>
suna agent resume <agent-id>
```

### Task Management

```bash
# Submit task
suna task submit --agent <agent-id> "task description" [--priority N] [--wait]

# Get task status
suna task status <task-id> [--format info|json]

# Cancel task
suna task cancel <task-id>

# List tasks
suna task list [--agent AGENT_ID] [--status STATUS] [--limit N] [--format table|json]
```

### Workflow Management

```bash
# List workflows
suna workflow list [--format table|json]

# Create workflow
suna workflow create --name NAME --definition '{"steps": [...]}'
# Or from file:
suna workflow create --name NAME --definition workflow.json

# Get workflow details
suna workflow get <workflow-id>

# Run workflow
suna workflow run <workflow-id> [--inputs '{"key": "value"}']
# Or from file:
suna workflow run <workflow-id> --inputs inputs.json

# Delete workflow
suna workflow delete <workflow-id>
```

### Tool Management

```bash
# List all tools
suna tool list [--category CATEGORY] [--format table|json]

# Get tool information
suna tool info <tool-name>
```

### Logs

```bash
# Stream task logs
suna logs --follow --task-id <task-id>

# View agent logs
suna logs --agent-id <agent-id> [--tail N]
```

### Configuration

```bash
# Set configuration value
suna config set <key> <value>

# Get configuration value
suna config get <key>

# List all configuration
suna config list

# Delete configuration key
suna config delete <key>

# Clear all configuration
suna config clear
```

## 🎨 Output Formats

Most list commands support multiple output formats:

- `table` (default): Rich formatted tables
- `json`: JSON output for scripting

Example:

```bash
# Table format (default)
suna agent list

# JSON format
suna agent list --format json
```

## ⚙️ Configuration

Configuration is stored in `~/.suna/config.json`

Available configuration keys:

- `api_key`: Your Suna API key
- `base_url`: API base URL (default: http://localhost:8000)
- `default_workspace`: Default workspace ID

Set configuration:

```bash
suna config set base_url https://api.suna.so
```

## 🔄 Streaming

Stream real-time task updates:

```bash
# Stream task events
suna agent run <agent-id> "task description" --stream

# Follow task logs
suna logs --follow --task-id <task-id>
```

## 💡 Examples

### Create and run a research agent

```bash
# Create agent
suna agent create \
  --name "Research Assistant" \
  --type research \
  --capability web_search \
  --system-prompt "You are a helpful research assistant."

# Run task (wait for completion)
suna agent run agent-123 "Research quantum computing trends" --wait

# Run task with streaming
suna agent run agent-123 "Analyze AI market" --stream
```

### Manage tasks

```bash
# Submit task
suna task submit --agent agent-123 "Summarize latest AI papers" --priority 8

# Check status
suna task status task-456

# List all running tasks
suna task list --status running

# Cancel task
suna task cancel task-456
```

### Create and run a workflow

```bash
# Create workflow from JSON file
cat > workflow.json <<EOF
{
  "steps": [
    {"id": "research", "agent": "agent-1", "task": "Research topic"},
    {"id": "summarize", "agent": "agent-2", "task": "Summarize findings", "depends_on": ["research"]}
  ]
}
EOF

suna workflow create --name "Research Pipeline" --definition workflow.json

# Run workflow
suna workflow run workflow-789 --inputs '{"topic": "AI trends"}'
```

## 🐛 Troubleshooting

### Authentication Issues

If you get authentication errors:

```bash
# Check status
suna status

# Re-login
suna logout
suna login
```

### Connection Issues

If you can't connect to the API:

```bash
# Check base URL
suna config get base_url

# Update base URL if needed
suna config set base_url http://localhost:8000
```

## 📄 License

MIT License - see [LICENSE](../python/LICENSE) file for details.

## 🔗 Links

- **Homepage**: [https://suna.so](https://suna.so)
- **Documentation**: [https://docs.suna.so](https://docs.suna.so)
- **Python SDK**: [../python/](../python/)
- **Support**: [support@suna.so](mailto:support@suna.so)
