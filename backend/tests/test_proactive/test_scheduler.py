"""
Tests for proactive scheduler.
"""

import pytest
from proactive.scheduler import Scheduler


@pytest.mark.asyncio
async def test_create_schedule():
    """Test creating a scheduled task."""
    scheduler = Scheduler()
    
    schedule = await scheduler.create(
        name="Daily Report",
        workspace_id="ws-123",
        agent_id="agent-123",
        task_description="Generate daily report",
        cron_expression="0 9 * * *",
        timezone="UTC"
    )
    
    assert schedule is not None
    assert schedule.name == "Daily Report"
    assert schedule.cron_expression == "0 9 * * *"
    assert schedule.is_active is True


@pytest.mark.asyncio
async def test_invalid_cron_expression():
    """Test creating a schedule with invalid cron expression."""
    scheduler = Scheduler()
    
    with pytest.raises(ValueError, match="Invalid cron"):
        await scheduler.create(
            "Test", "ws-1", "agent-1", "Task", "invalid cron", "UTC"
        )


@pytest.mark.asyncio
async def test_list_schedules():
    """Test listing schedules."""
    scheduler = Scheduler()
    
    await scheduler.create(
        "Schedule 1", "ws-1", "agent-1", "Task 1", "0 9 * * *"
    )
    await scheduler.create(
        "Schedule 2", "ws-1", "agent-2", "Task 2", "0 10 * * *"
    )
    
    schedules = await scheduler.list("ws-1")
    assert len(schedules) == 2


@pytest.mark.asyncio
async def test_pause_resume_schedule():
    """Test pausing and resuming a schedule."""
    scheduler = Scheduler()
    
    schedule = await scheduler.create(
        "Test", "ws-1", "agent-1", "Task", "0 9 * * *"
    )
    
    # Pause
    paused = await scheduler.pause(schedule.id)
    assert paused.is_active is False
    
    # Resume
    resumed = await scheduler.resume(schedule.id)
    assert resumed.is_active is True


@pytest.mark.asyncio
async def test_run_now():
    """Test running a schedule immediately."""
    scheduler = Scheduler()
    
    schedule = await scheduler.create(
        "Test", "ws-1", "agent-1", "Task", "0 9 * * *"
    )
    
    task_id = await scheduler.run_now(schedule.id)
    assert task_id is not None


@pytest.mark.asyncio
async def test_delete_schedule():
    """Test deleting a schedule."""
    scheduler = Scheduler()
    
    schedule = await scheduler.create(
        "Test", "ws-1", "agent-1", "Task", "0 9 * * *"
    )
    
    success = await scheduler.delete(schedule.id)
    assert success is True
    
    result = await scheduler.get(schedule.id)
    assert result is None
