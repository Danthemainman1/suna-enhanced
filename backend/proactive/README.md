# Proactive Agent System

Autonomous proactive agents that monitor, trigger, and act without user intervention.

## Overview

The proactive agent system enables autonomous operation through:
- **Monitors**: Continuously check conditions and trigger agents when conditions are met
- **Triggers**: Event-based firing of agents from various sources (webhooks, schedules, etc.)
- **Scheduler**: Cron-based scheduled task execution
- **Webhooks**: Incoming webhook endpoints that trigger agents
- **Suggestions**: AI-powered task recommendations based on user patterns

## Architecture

```
backend/proactive/
├── __init__.py           # Module exports
├── models.py             # Pydantic data models
├── monitor.py            # Continuous monitoring system
├── triggers.py           # Event-based trigger management
├── scheduler.py          # Cron-based scheduling
├── webhooks.py           # Webhook endpoint management
├── suggestions.py        # AI-powered suggestions
├── api.py                # FastAPI router with endpoints
└── worker.py             # Background worker for automation
```

## API Endpoints

### Monitors

Continuously check conditions and trigger agents when met.

```
POST   /api/proactive/monitors              # Create monitor
GET    /api/proactive/monitors              # List monitors
GET    /api/proactive/monitors/{id}         # Get monitor
PATCH  /api/proactive/monitors/{id}         # Update monitor
DELETE /api/proactive/monitors/{id}         # Delete monitor
POST   /api/proactive/monitors/{id}/pause   # Pause monitor
POST   /api/proactive/monitors/{id}/resume  # Resume monitor
POST   /api/proactive/monitors/{id}/check   # Check now
GET    /api/proactive/monitors/{id}/history # Get history
```

**Example: Create a Monitor**
```json
POST /api/proactive/monitors
{
  "name": "Stock Price Monitor",
  "agent_id": "trading-agent-123",
  "workspace_id": "ws-456",
  "condition": "AAPL stock price > 150",
  "action": "Send alert and analyze",
  "check_interval": 300
}
```

### Triggers

Event-based triggers that fire agents.

```
POST   /api/proactive/triggers              # Create trigger
GET    /api/proactive/triggers              # List triggers
DELETE /api/proactive/triggers/{id}         # Delete trigger
POST   /api/proactive/triggers/{id}/fire    # Fire trigger manually
```

**Example: Create a Trigger**
```json
POST /api/proactive/triggers
{
  "name": "GitHub PR Trigger",
  "workspace_id": "ws-456",
  "trigger_type": "github",
  "config": {
    "repository": "owner/repo",
    "event": "pull_request"
  },
  "agent_id": "code-review-agent",
  "task_template": "Review PR #{pr_number}: {pr_title}"
}
```

### Schedules

Cron-based scheduled tasks.

```
POST   /api/proactive/schedules             # Create schedule
GET    /api/proactive/schedules             # List schedules
DELETE /api/proactive/schedules/{id}        # Delete schedule
POST   /api/proactive/schedules/{id}/run    # Run now
POST   /api/proactive/schedules/{id}/pause  # Pause schedule
POST   /api/proactive/schedules/{id}/resume # Resume schedule
```

**Example: Create a Schedule**
```json
POST /api/proactive/schedules
{
  "name": "Daily Report",
  "workspace_id": "ws-456",
  "agent_id": "report-agent",
  "task_description": "Generate daily metrics report",
  "cron_expression": "0 9 * * *",
  "timezone": "America/New_York"
}
```

### Webhooks

Incoming webhook endpoints.

```
POST   /api/proactive/webhooks                        # Create webhook
GET    /api/proactive/webhooks                        # List webhooks
DELETE /api/proactive/webhooks/{id}                   # Delete webhook
POST   /api/proactive/webhooks/{id}/regenerate-secret # Regenerate secret
POST   /api/hooks/{url_path}                          # Incoming webhook
```

**Example: Create a Webhook**
```json
POST /api/proactive/webhooks
{
  "workspace_id": "ws-456",
  "name": "Deploy Webhook",
  "trigger_id": "trigger-789"
}

Response:
{
  "id": "webhook-abc",
  "url_path": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "secret": "abc123...",
  "webhook_url": "https://api.suna.so/api/hooks/f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

### Suggestions

AI-powered task suggestions.

```
GET    /api/proactive/suggestions              # Get suggestions
POST   /api/proactive/suggestions/{id}/accept  # Accept suggestion
POST   /api/proactive/suggestions/{id}/dismiss # Dismiss suggestion
GET    /api/proactive/patterns                 # Analyze patterns
```

## Background Worker

The background worker automatically:
- Checks active monitors at their configured intervals
- Executes scheduled tasks at their cron times
- Uses Redis for coordination and persistence

### Lifecycle

The worker is automatically started and stopped with the application:

```python
# Started in lifespan context
from proactive import worker as proactive_worker
await proactive_worker.initialize()

# Stopped on shutdown
await proactive_worker.cleanup()
```

## Data Models

### Monitor
```python
Monitor(
    id="mon-123",
    name="Stock Monitor",
    agent_id="agent-456",
    workspace_id="ws-789",
    condition="stock price > 100",
    action="alert and analyze",
    check_interval=300,
    is_active=True,
    last_check=None,
    last_triggered=None,
    trigger_count=0
)
```

### Trigger
```python
Trigger(
    id="trig-123",
    name="Webhook Trigger",
    workspace_id="ws-789",
    trigger_type=TriggerType.WEBHOOK,
    config={"url": "..."},
    agent_id="agent-456",
    task_template="Process: {event}",
    is_active=True
)
```

### ScheduledTask
```python
ScheduledTask(
    id="sched-123",
    name="Daily Report",
    workspace_id="ws-789",
    agent_id="agent-456",
    task_description="Generate report",
    cron_expression="0 9 * * *",
    timezone="UTC",
    is_active=True,
    next_run=datetime(...),
    last_run=None
)
```

## Usage Examples

### Python SDK

```python
from proactive import ProactiveMonitor, Scheduler, WebhookManager

# Create a monitor
monitor_manager = ProactiveMonitor()
monitor = await monitor_manager.create(
    name="System Health Check",
    agent_id="health-agent",
    workspace_id="ws-123",
    condition="CPU usage > 80%",
    action="Investigate and optimize",
    check_interval=60  # Check every minute
)

# Create a scheduled task
scheduler = Scheduler()
schedule = await scheduler.create(
    name="Weekly Backup",
    workspace_id="ws-123",
    agent_id="backup-agent",
    task_description="Backup all databases",
    cron_expression="0 0 * * 0",  # Every Sunday at midnight
    timezone="UTC"
)

# Create a webhook
webhook_manager = WebhookManager()
webhook = await webhook_manager.create(
    workspace_id="ws-123",
    name="CI/CD Webhook",
    trigger_id="trigger-456"
)
print(f"Webhook URL: https://api.suna.so/api/hooks/{webhook.url_path}")
```

### REST API

```bash
# Create a monitor
curl -X POST https://api.suna.so/api/proactive/monitors \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Response Time Monitor",
    "agent_id": "performance-agent",
    "workspace_id": "ws-123",
    "condition": "API response time > 500ms",
    "action": "Investigate slow endpoints",
    "check_interval": 300
  }'

# Fire a trigger
curl -X POST https://api.suna.so/api/proactive/triggers/trigger-123/fire \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "event": "deployment",
      "version": "v1.2.3"
    }
  }'
```

## Security

- All API endpoints require JWT authentication
- Webhook signature verification using HMAC-SHA256
- Secrets can be regenerated at any time
- Rate limiting applied to sensitive endpoints
- Input validation through Pydantic models

## Testing

Run tests:
```bash
cd backend
python -m pytest tests/test_proactive/ -v
```

## Dependencies

- FastAPI for REST API
- Pydantic v2 for data validation
- croniter for cron expression parsing
- pytz for timezone handling
- Redis for coordination and persistence

## Future Enhancements

- [ ] Database persistence (currently Redis-only)
- [ ] Advanced condition evaluation (currently placeholder)
- [ ] Multi-agent coordination in monitors
- [ ] Webhook payload transformation
- [ ] Advanced AI suggestions with ML models
- [ ] Monitor templates and presets
- [ ] Trigger chaining and workflows
- [ ] Performance metrics and analytics
