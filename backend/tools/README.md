# Suna Enhanced Tools System

## Overview

The Suna Enhanced Tools System provides a comprehensive ecosystem of 50+ production-ready integrations across 10 categories. Every tool is built with full async support, proper error handling, exponential backoff retries, and rate limiting.

## Architecture

### Base Components

- **`base.py`**: Abstract base classes (`Tool`, `BaseTool`) with standardized interfaces
- **`result.py`**: Standardized `ToolResult` class for consistent output handling
- **`registry.py`**: Central registry with auto-discovery and filtering capabilities
- **`exceptions.py`**: Custom exception hierarchy for tool-specific errors

### Tool Categories

1. **Communication** (5 tools): Slack, Discord, Telegram, Email, Twilio SMS
2. **Productivity** (6 tools): Notion, Airtable, Google Workspace, Google Calendar, Trello, Todoist
3. **Development** (6 tools): GitHub, GitLab, Jira, Linear, Vercel, Docker
4. **Data** (6 tools): PostgreSQL, MongoDB, Redis, Elasticsearch, Supabase, CSV Handler
5. **AI/ML** (5 tools): Anthropic Claude, OpenAI, HuggingFace, Replicate, Stability AI
6. **Browser** (4 tools): Web Scraper, Playwright Browser, Screenshot, PDF Generator
7. **Finance** (3 tools): Stripe, PayPal, Crypto
8. **Storage** (4 tools): S3, Cloudflare R2, Google Cloud Storage, Local Storage
9. **Search** (4 tools): Google Search, Bing Search, DuckDuckGo, Wikipedia
10. **Utilities** (7 tools): HTTP Client, JSON Handler, Text Processing, DateTime, Math, Code Executor, Shell Executor

## Usage

### Basic Tool Usage

```python
from tools.communication.slack import SlackTool
from tools.registry import get_registry

# Direct instantiation
slack = SlackTool(token="xoxb-your-token")

# Execute an action
result = await slack.execute(
    action="send_message",
    channel="C0123456789",
    text="Hello from Suna!"
)

if result.success:
    print(f"Message sent: {result.output}")
else:
    print(f"Error: {result.error}")
```

### Using the Registry

```python
from tools.registry import get_registry
from tools.communication.slack import SlackTool

# Get global registry
registry = get_registry()

# Register a tool
slack = SlackTool(token="xoxb-your-token")
registry.register(slack)

# Get tool from registry
tool = registry.get("slack")

# List all tools
all_tools = registry.list_tools()

# Filter by category
comm_tools = registry.get_tools_by_category("communication")

# Filter by capability
messaging_tools = registry.get_tools_by_capability("messaging")

# Search tools
search_results = registry.search("slack")
```

### Auto-Discovery

```python
from tools.registry import get_registry

registry = get_registry()

# Auto-discover all tools (those that don't require config)
count = registry.auto_discover_tools(base_package="tools")
print(f"Discovered {count} tools")
```

## Tool Features

### Async Support

All tools are fully async and use `async/await`:

```python
result = await tool.execute(action="...", **params)
```

### Error Handling

Tools use custom exceptions for better error handling:

```python
from tools.exceptions import (
    ToolAuthenticationError,
    ToolExecutionError,
    ToolRateLimitError,
    ToolTimeoutError
)

try:
    result = await tool.execute(**params)
except ToolAuthenticationError as e:
    print(f"Authentication failed: {e}")
except ToolRateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except ToolExecutionError as e:
    print(f"Execution failed: {e}")
```

### Retries with Exponential Backoff

Most tools implement automatic retries with exponential backoff:

```python
# Automatically retries up to 3 times with exponential backoff
result = await tool._make_request(
    method="POST",
    endpoint="api/endpoint",
    data={"key": "value"},
    retries=3  # Default
)
```

### Rate Limiting

Tools handle rate limiting gracefully:

```python
# Automatically waits and retries when rate limited
result = await slack.send_message(
    channel="C0123456789",
    text="Message"
)
```

## Tool Development

### Creating a New Tool

```python
from typing import List
from tools.base import BaseTool, ToolCategory, ToolParameter
from tools.result import ToolResult
from tools.exceptions import ToolAuthenticationError

class MyCustomTool(BaseTool):
    """My custom tool description."""
    
    name = "my_tool"
    description = "Does something useful"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.api_key = config.get("api_key")
        
        if not self.api_key:
            raise ToolAuthenticationError(
                "API key required",
                tool_name=self.name
            )
    
    def get_capabilities(self) -> List[str]:
        return ["capability1", "capability2"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=["action1", "action2"]
            ),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action")
        
        # Implement your logic here
        
        return ToolResult.success_result(
            output={"status": "completed"},
            tool_name=self.name,
            metadata={"action": action}
        )
```

## Testing

Tests are located in `backend/tests/test_tools/`:

```bash
# Run all tool tests
pytest backend/tests/test_tools/ -v

# Run specific test file
pytest backend/tests/test_tools/test_communication_tools.py -v

# Run with coverage
pytest backend/tests/test_tools/ --cov=tools --cov-report=html
```

## Technical Requirements

- **Python**: 3.11+
- **Type Hints**: Full type annotations throughout
- **Async/Await**: All I/O operations are async
- **Pydantic**: v2 models for validation
- **httpx**: For async HTTP requests
- **Comprehensive Docstrings**: All classes and methods documented

## Tool Count

Total: **50 tools** across **10 categories**

## Examples

### Slack Integration

```python
from tools.communication.slack import SlackTool

slack = SlackTool(token="xoxb-your-token")

# Send a message
result = await slack.send_message(
    channel="general",
    text="Hello World!"
)

# Send a DM
result = await slack.send_dm(
    user_id="U0123456789",
    text="Private message"
)

# Add a reaction
result = await slack.add_reaction(
    channel="C0123456789",
    timestamp="1234567890.123456",
    emoji="thumbsup"
)
```

### GitHub Integration

```python
from tools.development.github_tool import GitHubTool

github = GitHubTool(token="ghp_your_token")

# Create a repository
result = await github.create_repo(
    name="my-repo",
    private=True,
    description="My awesome repo"
)

# Create an issue
result = await github.create_issue(
    owner="username",
    repo="my-repo",
    title="Bug Report",
    body="Found a bug..."
)

# Create a pull request
result = await github.create_pr(
    owner="username",
    repo="my-repo",
    title="Feature: Add new feature",
    head="feature-branch",
    base="main",
    body="This PR adds..."
)
```

### Notion Integration

```python
from tools.productivity.notion import NotionTool

notion = NotionTool(token="secret_your_token")

# Create a page
result = await notion.create_page(
    parent_id="parent_page_id",
    title="New Page",
    content=[
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": "Page content"}}]
            }
        }
    ]
)

# Search workspace
result = await notion.search(query="project")

# Query database
result = await notion.query_database(
    database_id="database_id",
    filter_obj={"property": "Status", "select": {"equals": "In Progress"}}
)
```

## Contributing

When adding new tools:

1. Follow the existing tool structure
2. Implement full async support
3. Add proper error handling with custom exceptions
4. Implement retries with exponential backoff
5. Add comprehensive docstrings
6. Include type hints
7. Add tests in `backend/tests/test_tools/`
8. Update this README

## License

Apache 2.0
