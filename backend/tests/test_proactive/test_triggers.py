"""
Tests for proactive triggers.
"""

import pytest
from proactive.triggers import TriggerManager
from proactive.models import TriggerType


@pytest.mark.asyncio
async def test_create_trigger():
    """Test creating a trigger."""
    trigger_manager = TriggerManager()
    
    trigger = await trigger_manager.create(
        name="Test Trigger",
        workspace_id="ws-123",
        trigger_type=TriggerType.WEBHOOK,
        config={"url": "https://example.com"},
        agent_id="agent-123",
        task_template="Process webhook: {event}"
    )
    
    assert trigger is not None
    assert trigger.name == "Test Trigger"
    assert trigger.trigger_type == TriggerType.WEBHOOK
    assert trigger.is_active is True


@pytest.mark.asyncio
async def test_fire_trigger():
    """Test firing a trigger."""
    trigger_manager = TriggerManager()
    
    trigger = await trigger_manager.create(
        "Test Trigger", "ws-1", TriggerType.WEBHOOK,
        {}, "agent-1", "Task: {action}"
    )
    
    # Fire the trigger
    task_id = await trigger_manager.fire(trigger.id, {"action": "test"})
    assert task_id is not None


@pytest.mark.asyncio
async def test_fire_inactive_trigger():
    """Test firing an inactive trigger."""
    trigger_manager = TriggerManager()
    
    trigger = await trigger_manager.create(
        "Test Trigger", "ws-1", TriggerType.WEBHOOK,
        {}, "agent-1", "Task"
    )
    
    # Make it inactive
    trigger.is_active = False
    
    # Try to fire it
    with pytest.raises(ValueError, match="not active"):
        await trigger_manager.fire(trigger.id, {})


@pytest.mark.asyncio
async def test_list_triggers():
    """Test listing triggers."""
    trigger_manager = TriggerManager()
    
    await trigger_manager.create(
        "Trigger 1", "ws-1", TriggerType.WEBHOOK, {}, "agent-1", "Task 1"
    )
    await trigger_manager.create(
        "Trigger 2", "ws-1", TriggerType.SCHEDULE, {}, "agent-2", "Task 2"
    )
    
    triggers = await trigger_manager.list("ws-1")
    assert len(triggers) == 2


@pytest.mark.asyncio
async def test_delete_trigger():
    """Test deleting a trigger."""
    trigger_manager = TriggerManager()
    
    trigger = await trigger_manager.create(
        "Test Trigger", "ws-1", TriggerType.WEBHOOK, {}, "agent-1", "Task"
    )
    
    success = await trigger_manager.delete(trigger.id)
    assert success is True
    
    # Verify it's gone
    result = await trigger_manager.get(trigger.id)
    assert result is None
