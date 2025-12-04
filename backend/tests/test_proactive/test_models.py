"""
Tests for proactive models.
"""

import pytest
from datetime import datetime
from proactive.models import (
    Monitor,
    MonitorEvent,
    Trigger,
    TriggerType,
    ScheduledTask,
    Webhook,
    TaskSuggestion,
    CreateMonitorRequest,
)


def test_monitor_model():
    """Test Monitor model."""
    monitor = Monitor(
        id="mon-123",
        name="Test Monitor",
        agent_id="agent-123",
        workspace_id="ws-123",
        condition="stock > 100",
        action="alert",
        check_interval=300,
        is_active=True,
        last_check=None,
        last_triggered=None,
        trigger_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={}
    )
    
    assert monitor.id == "mon-123"
    assert monitor.name == "Test Monitor"
    assert monitor.is_active is True


def test_trigger_type_enum():
    """Test TriggerType enum."""
    assert TriggerType.WEBHOOK == "webhook"
    assert TriggerType.SCHEDULE == "schedule"
    assert TriggerType.EMAIL == "email"


def test_create_monitor_request():
    """Test CreateMonitorRequest model."""
    request = CreateMonitorRequest(
        name="Test Monitor",
        agent_id="agent-123",
        workspace_id="ws-123",
        condition="test condition",
        action="test action",
        check_interval=600
    )
    
    assert request.name == "Test Monitor"
    assert request.check_interval == 600


def test_scheduled_task_model():
    """Test ScheduledTask model."""
    task = ScheduledTask(
        id="task-123",
        name="Daily Report",
        workspace_id="ws-123",
        agent_id="agent-123",
        task_description="Generate report",
        cron_expression="0 9 * * *",
        timezone="UTC",
        is_active=True,
        next_run=None,
        last_run=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={}
    )
    
    assert task.name == "Daily Report"
    assert task.cron_expression == "0 9 * * *"


def test_webhook_model():
    """Test Webhook model."""
    webhook = Webhook(
        id="hook-123",
        workspace_id="ws-123",
        name="Test Webhook",
        url_path="unique-path",
        secret="secret-key",
        trigger_id="trigger-123",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={}
    )
    
    assert webhook.name == "Test Webhook"
    assert webhook.secret == "secret-key"


def test_task_suggestion_model():
    """Test TaskSuggestion model."""
    suggestion = TaskSuggestion(
        id="sug-123",
        workspace_id="ws-123",
        user_id="user-123",
        title="Test Suggestion",
        description="Test description",
        suggested_agent_id="agent-123",
        confidence=0.85,
        reason="Test reason",
        created_at=datetime.utcnow(),
        dismissed=False,
        accepted=False,
        metadata={}
    )
    
    assert suggestion.title == "Test Suggestion"
    assert suggestion.confidence == 0.85
    assert 0.0 <= suggestion.confidence <= 1.0
