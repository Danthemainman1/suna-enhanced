"""
Tests for proactive monitors.
"""

import pytest
from datetime import datetime
from proactive.monitor import ProactiveMonitor


@pytest.mark.asyncio
async def test_create_monitor():
    """Test creating a monitor."""
    monitor_manager = ProactiveMonitor()
    
    monitor = await monitor_manager.create(
        name="Test Monitor",
        agent_id="test-agent-123",
        workspace_id="ws-123",
        condition="stock price > 100",
        action="Send alert"
    )
    
    assert monitor is not None
    assert monitor.name == "Test Monitor"
    assert monitor.agent_id == "test-agent-123"
    assert monitor.workspace_id == "ws-123"
    assert monitor.is_active is True
    assert monitor.trigger_count == 0


@pytest.mark.asyncio
async def test_list_monitors():
    """Test listing monitors for a workspace."""
    monitor_manager = ProactiveMonitor()
    
    # Create multiple monitors
    await monitor_manager.create(
        "Monitor 1", "agent-1", "ws-1", "condition 1", "action 1"
    )
    await monitor_manager.create(
        "Monitor 2", "agent-2", "ws-1", "condition 2", "action 2"
    )
    await monitor_manager.create(
        "Monitor 3", "agent-3", "ws-2", "condition 3", "action 3"
    )
    
    # List monitors for ws-1
    monitors = await monitor_manager.list("ws-1")
    assert len(monitors) == 2
    
    # List monitors for ws-2
    monitors = await monitor_manager.list("ws-2")
    assert len(monitors) == 1


@pytest.mark.asyncio
async def test_get_monitor():
    """Test getting a specific monitor."""
    monitor_manager = ProactiveMonitor()
    
    created = await monitor_manager.create(
        "Test Monitor", "agent-1", "ws-1", "condition", "action"
    )
    
    # Get the monitor
    monitor = await monitor_manager.get(created.id)
    assert monitor is not None
    assert monitor.id == created.id
    assert monitor.name == "Test Monitor"
    
    # Try to get non-existent monitor
    monitor = await monitor_manager.get("non-existent")
    assert monitor is None


@pytest.mark.asyncio
async def test_update_monitor():
    """Test updating a monitor."""
    monitor_manager = ProactiveMonitor()
    
    created = await monitor_manager.create(
        "Test Monitor", "agent-1", "ws-1", "condition", "action"
    )
    
    # Update the monitor
    updated = await monitor_manager.update(
        created.id,
        name="Updated Monitor",
        check_interval=600
    )
    
    assert updated is not None
    assert updated.name == "Updated Monitor"
    assert updated.check_interval == 600
    
    # Try to update non-existent monitor
    updated = await monitor_manager.update("non-existent", name="Test")
    assert updated is None


@pytest.mark.asyncio
async def test_pause_resume_monitor():
    """Test pausing and resuming a monitor."""
    monitor_manager = ProactiveMonitor()
    
    created = await monitor_manager.create(
        "Test Monitor", "agent-1", "ws-1", "condition", "action"
    )
    
    # Pause the monitor
    paused = await monitor_manager.pause(created.id)
    assert paused is not None
    assert paused.is_active is False
    
    # Resume the monitor
    resumed = await monitor_manager.resume(created.id)
    assert resumed is not None
    assert resumed.is_active is True


@pytest.mark.asyncio
async def test_delete_monitor():
    """Test deleting a monitor."""
    monitor_manager = ProactiveMonitor()
    
    created = await monitor_manager.create(
        "Test Monitor", "agent-1", "ws-1", "condition", "action"
    )
    
    # Delete the monitor
    success = await monitor_manager.delete(created.id)
    assert success is True
    
    # Verify it's gone
    monitor = await monitor_manager.get(created.id)
    assert monitor is None
    
    # Try to delete non-existent monitor
    success = await monitor_manager.delete("non-existent")
    assert success is False


@pytest.mark.asyncio
async def test_check_now():
    """Test manually triggering a monitor check."""
    monitor_manager = ProactiveMonitor()
    
    created = await monitor_manager.create(
        "Test Monitor", "agent-1", "ws-1", "condition", "action"
    )
    
    # Check now
    event = await monitor_manager.check_now(created.id)
    assert event is not None
    assert event.monitor_id == created.id
    
    # Try to check non-existent monitor
    event = await monitor_manager.check_now("non-existent")
    assert event is None


@pytest.mark.asyncio
async def test_get_history():
    """Test getting monitor event history."""
    monitor_manager = ProactiveMonitor()
    
    created = await monitor_manager.create(
        "Test Monitor", "agent-1", "ws-1", "condition", "action"
    )
    
    # Trigger some checks
    await monitor_manager.check_now(created.id)
    await monitor_manager.check_now(created.id)
    
    # Get history
    history = await monitor_manager.get_history(created.id, limit=10)
    assert len(history) == 2
