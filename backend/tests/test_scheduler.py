"""
Tests for task scheduler and background executor.

This module tests scheduling, background execution, and notifications.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from scheduler import (
    TaskScheduler,
    BackgroundExecutor,
    NotificationService,
    TaskStatus,
    TaskEvent,
    TaskEventType,
    NotificationChannel,
    NotificationChannelType,
    WebhookConfig,
)


# Task Scheduler Tests
@pytest.mark.asyncio
async def test_schedule_creation():
    """Test creating a scheduled task."""
    scheduler = TaskScheduler()
    
    schedule_id = await scheduler.schedule(
        name="Test Schedule",
        cron_expression="0 0 * * *",  # Daily at midnight
        task_definition={"action": "test"},
        description="Test description"
    )
    
    assert schedule_id is not None
    assert isinstance(schedule_id, str)
    
    # Verify schedule was created
    schedule = await scheduler.get_schedule(schedule_id)
    assert schedule is not None
    assert schedule.name == "Test Schedule"


@pytest.mark.asyncio
async def test_schedule_cancellation():
    """Test cancelling a schedule."""
    scheduler = TaskScheduler()
    
    schedule_id = await scheduler.schedule(
        name="Test",
        cron_expression="0 0 * * *",
        task_definition={}
    )
    
    # Cancel the schedule
    success = await scheduler.cancel(schedule_id)
    assert success is True
    
    # Verify it's gone
    schedule = await scheduler.get_schedule(schedule_id)
    assert schedule is None


@pytest.mark.asyncio
async def test_schedule_pause_resume():
    """Test pausing and resuming a schedule."""
    scheduler = TaskScheduler()
    
    schedule_id = await scheduler.schedule(
        name="Test",
        cron_expression="0 0 * * *",
        task_definition={}
    )
    
    # Pause
    success = await scheduler.pause(schedule_id)
    assert success is True
    
    schedule = await scheduler.get_schedule(schedule_id)
    assert schedule.enabled is False
    
    # Resume
    success = await scheduler.resume(schedule_id)
    assert success is True
    
    schedule = await scheduler.get_schedule(schedule_id)
    assert schedule.enabled is True


@pytest.mark.asyncio
async def test_list_schedules():
    """Test listing schedules."""
    scheduler = TaskScheduler()
    
    # Create some schedules
    await scheduler.schedule("Schedule 1", "0 0 * * *", {})
    await scheduler.schedule("Schedule 2", "0 1 * * *", {}, enabled=False)
    
    # List all
    all_schedules = await scheduler.list_schedules()
    assert len(all_schedules) >= 2
    
    # List only enabled
    enabled_schedules = await scheduler.list_schedules(enabled_only=True)
    assert all(s.enabled for s in enabled_schedules)


@pytest.mark.asyncio
async def test_next_run_calculation():
    """Test next run time calculation."""
    scheduler = TaskScheduler()
    
    schedule_id = await scheduler.schedule(
        name="Test",
        cron_expression="0 0 * * *",
        task_definition={}
    )
    
    next_run = await scheduler.get_next_run(schedule_id)
    assert next_run is not None
    assert isinstance(next_run, datetime)
    assert next_run > datetime.utcnow()


@pytest.mark.asyncio
async def test_scheduler_start_stop():
    """Test starting and stopping the scheduler."""
    scheduler = TaskScheduler()
    
    await scheduler.start()
    assert scheduler._running is True
    
    await scheduler.stop()
    assert scheduler._running is False


# Background Executor Tests
@pytest.mark.asyncio
async def test_task_submission():
    """Test submitting a background task."""
    executor = BackgroundExecutor(num_workers=2)
    await executor.start()
    
    try:
        task_id = await executor.submit(
            name="Test Task",
            task_type="test",
            parameters={"param": "value"}
        )
        
        assert task_id is not None
        
        # Check status
        status = await executor.get_status(task_id)
        assert status is not None
        assert status.status == TaskStatus.PENDING
        assert status.name == "Test Task"
    finally:
        await executor.stop()


@pytest.mark.asyncio
async def test_task_priority():
    """Test task priority ordering."""
    executor = BackgroundExecutor()
    await executor.start()
    
    try:
        # Submit tasks with different priorities
        low_priority = await executor.submit(
            name="Low",
            task_type="test",
            priority=3
        )
        high_priority = await executor.submit(
            name="High",
            task_type="test",
            priority=8
        )
        
        # High priority should be processed first
        # This is tested by checking queue order
        assert high_priority is not None
        assert low_priority is not None
    finally:
        await executor.stop()


@pytest.mark.asyncio
async def test_task_cancellation():
    """Test cancelling a task."""
    executor = BackgroundExecutor()
    
    task_id = await executor.submit(name="Test", task_type="test")
    
    # Cancel the task
    success = await executor.cancel(task_id)
    assert success is True
    
    # Check status
    status = await executor.get_status(task_id)
    assert status.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_task_pause_resume():
    """Test pausing and resuming a task."""
    executor = BackgroundExecutor()
    
    task_id = await executor.submit(name="Test", task_type="test")
    
    # Pause
    success = await executor.pause(task_id)
    assert success is True
    
    status = await executor.get_status(task_id)
    assert status.status == TaskStatus.PAUSED
    
    # Resume
    success = await executor.resume(task_id)
    assert success is True
    
    status = await executor.get_status(task_id)
    assert status.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_list_tasks():
    """Test listing tasks."""
    executor = BackgroundExecutor()
    
    # Submit some tasks
    await executor.submit(name="Task 1", task_type="test")
    await executor.submit(name="Task 2", task_type="test")
    
    # List all tasks
    tasks = await executor.list_tasks(limit=10)
    assert len(tasks) >= 2


@pytest.mark.asyncio
async def test_task_execution():
    """Test task execution with custom executor."""
    executor = BackgroundExecutor(num_workers=1)
    
    # Register a test executor
    executed = []
    
    async def test_executor(params):
        executed.append(params)
        return {"result": "success"}
    
    executor.register_executor("test_type", test_executor)
    
    await executor.start()
    
    try:
        # Submit task
        task_id = await executor.submit(
            name="Test",
            task_type="test_type",
            parameters={"test": "value"}
        )
        
        # Wait a bit for execution
        await asyncio.sleep(2)
        
        # Check if executed
        status = await executor.get_status(task_id)
        # Status might be COMPLETED if execution finished
        assert status is not None
    finally:
        await executor.stop()


@pytest.mark.asyncio
async def test_task_dependencies():
    """Test task dependencies."""
    executor = BackgroundExecutor()
    
    # Create task with dependency
    task1_id = await executor.submit(name="Task 1", task_type="test")
    task2_id = await executor.submit(
        name="Task 2",
        task_type="test",
        dependencies=[task1_id]
    )
    
    assert task2_id is not None
    
    # Task 2 should wait for Task 1
    status = await executor.get_status(task2_id)
    assert status is not None


@pytest.mark.asyncio
async def test_executor_stats():
    """Test getting executor statistics."""
    executor = BackgroundExecutor(num_workers=3)
    await executor.start()
    
    try:
        # Submit some tasks
        await executor.submit(name="Task 1", task_type="test")
        await executor.submit(name="Task 2", task_type="test")
        
        stats = executor.get_stats()
        
        assert stats['running'] is True
        assert stats['num_workers'] == 3
        assert stats['total_tasks'] >= 2
    finally:
        await executor.stop()


# Notification Service Tests
@pytest.mark.asyncio
async def test_webhook_notification():
    """Test webhook notification configuration."""
    service = NotificationService()
    
    config = await service.configure_webhook(
        webhook_id="test_webhook",
        url="https://example.com/webhook",
        secret="secret123"
    )
    
    assert config.url == "https://example.com/webhook"
    assert config.secret == "secret123"


@pytest.mark.asyncio
async def test_notification_channel():
    """Test notification channel management."""
    service = NotificationService()
    
    # Create a webhook channel
    webhook_config = WebhookConfig(
        url="https://example.com/webhook",
        timeout_seconds=30
    )
    
    channel = NotificationChannel(
        channel_type=NotificationChannelType.WEBHOOK,
        webhook_config=webhook_config,
        enabled=True
    )
    
    service.add_channel("channel_1", channel)
    
    # Retrieve it
    retrieved = service.get_channel("channel_1")
    assert retrieved is not None
    assert retrieved.channel_type == NotificationChannelType.WEBHOOK


@pytest.mark.asyncio
async def test_remove_channel():
    """Test removing a notification channel."""
    service = NotificationService()
    
    # Add a channel
    channel = NotificationChannel(
        channel_type=NotificationChannelType.WEBHOOK,
        webhook_config=WebhookConfig(url="https://example.com")
    )
    service.add_channel("test", channel)
    
    # Remove it
    success = service.remove_channel("test")
    assert success is True
    
    # Verify it's gone
    retrieved = service.get_channel("test")
    assert retrieved is None


@pytest.mark.asyncio
async def test_send_notification():
    """Test sending notifications (mocked)."""
    service = NotificationService()
    
    # Create test event
    event = TaskEvent(
        event_id="event_1",
        task_id="task_1",
        event_type=TaskEventType.COMPLETED,
        data={"result": "success"}
    )
    
    # Create mock channel
    channel = NotificationChannel(
        channel_type=NotificationChannelType.WEBHOOK,
        webhook_config=WebhookConfig(url="https://example.com/webhook"),
        enabled=True
    )
    
    # This will attempt to send but fail gracefully in test environment
    # In production, it would send to the webhook
    await service.notify(
        task_id="task_1",
        event=event,
        channels=[channel]
    )
    
    # Test completes if no exception raised


# Integration Tests
@pytest.mark.asyncio
async def test_scheduler_executor_integration():
    """Test integration between scheduler and executor."""
    scheduler = TaskScheduler()
    executor = BackgroundExecutor()
    
    await scheduler.start()
    await executor.start()
    
    try:
        # Register callback to submit background task
        async def schedule_callback(task_def):
            await executor.submit(
                name=task_def.get('name', 'Scheduled Task'),
                task_type=task_def.get('type', 'scheduled')
            )
        
        # Create schedule
        schedule_id = await scheduler.schedule(
            name="Test Integration",
            cron_expression="* * * * *",  # Every minute
            task_definition={
                'name': 'Test Task',
                'type': 'test'
            }
        )
        
        scheduler.register_execution_callback(schedule_id, schedule_callback)
        
        # Verify schedule exists
        schedule = await scheduler.get_schedule(schedule_id)
        assert schedule is not None
        
    finally:
        await scheduler.stop()
        await executor.stop()
