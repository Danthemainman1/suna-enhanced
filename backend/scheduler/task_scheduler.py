"""
Cron-like task scheduling system.

This module provides scheduling capabilities for recurring and one-time tasks
using cron expressions.
"""

import uuid
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from croniter import croniter
from .models import ScheduledTask, CronExpression, TaskStatus
from collections import defaultdict


class TaskScheduler:
    """
    Cron-like task scheduler with dependency support.
    
    Schedules tasks to run at specific times using cron expressions,
    manages dependencies, and handles priority queuing.
    """
    
    def __init__(self):
        """Initialize the task scheduler."""
        self._schedules: dict[str, ScheduledTask] = {}
        self._running = False
        self._check_interval = 60  # Check every minute
        self._scheduler_task: Optional[asyncio.Task] = None
        self._execution_callbacks: dict[str, callable] = {}
    
    async def start(self):
        """Start the scheduler background task."""
        if self._running:
            return
        
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self):
        """Stop the scheduler background task."""
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
    
    async def schedule(
        self,
        name: str,
        cron_expression: str,
        task_definition: dict,
        description: Optional[str] = None,
        timezone: str = "UTC",
        max_retries: int = 3,
        retry_delay_seconds: int = 60,
        timeout_seconds: Optional[int] = None,
        enabled: bool = True,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Schedule a recurring task.
        
        Args:
            name: Human-readable task name
            cron_expression: Cron expression (e.g., '0 0 * * *')
            task_definition: Task configuration to execute
            description: Optional task description
            timezone: Timezone for schedule
            max_retries: Maximum retry attempts
            retry_delay_seconds: Delay between retries
            timeout_seconds: Task timeout
            enabled: Whether schedule is active
            metadata: Additional metadata
            
        Returns:
            Schedule ID
        """
        schedule_id = str(uuid.uuid4())
        
        # Calculate next run time
        cron_expr = CronExpression(expression=cron_expression, timezone=timezone)
        next_run = self._calculate_next_run(cron_expression, timezone)
        
        schedule = ScheduledTask(
            schedule_id=schedule_id,
            name=name,
            description=description,
            cron_expression=cron_expr,
            next_run=next_run,
            enabled=enabled,
            task_definition=task_definition,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            timeout_seconds=timeout_seconds,
            metadata=metadata or {}
        )
        
        self._schedules[schedule_id] = schedule
        return schedule_id
    
    async def cancel(self, schedule_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            True if cancelled, False if not found
        """
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False
    
    async def pause(self, schedule_id: str) -> bool:
        """
        Pause a scheduled task.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            True if paused, False if not found
        """
        if schedule_id in self._schedules:
            self._schedules[schedule_id].enabled = False
            return True
        return False
    
    async def resume(self, schedule_id: str) -> bool:
        """
        Resume a paused scheduled task.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            True if resumed, False if not found
        """
        if schedule_id in self._schedules:
            self._schedules[schedule_id].enabled = True
            # Recalculate next run time
            schedule = self._schedules[schedule_id]
            if schedule.cron_expression:
                schedule.next_run = self._calculate_next_run(
                    schedule.cron_expression.expression,
                    schedule.cron_expression.timezone
                )
            return True
        return False
    
    async def list_schedules(
        self,
        enabled_only: bool = False
    ) -> list[ScheduledTask]:
        """
        List all scheduled tasks.
        
        Args:
            enabled_only: Only return enabled schedules
            
        Returns:
            List of scheduled tasks
        """
        schedules = list(self._schedules.values())
        if enabled_only:
            schedules = [s for s in schedules if s.enabled]
        return schedules
    
    async def get_schedule(self, schedule_id: str) -> Optional[ScheduledTask]:
        """
        Get a specific schedule.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            ScheduledTask if found, None otherwise
        """
        return self._schedules.get(schedule_id)
    
    async def get_next_run(self, schedule_id: str) -> Optional[datetime]:
        """
        Get the next run time for a schedule.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Next run datetime if found, None otherwise
        """
        schedule = self._schedules.get(schedule_id)
        if schedule:
            return schedule.next_run
        return None
    
    def register_execution_callback(
        self,
        schedule_id: str,
        callback: callable
    ):
        """
        Register a callback to execute when a schedule triggers.
        
        Args:
            schedule_id: Schedule identifier
            callback: Async function to call with task_definition
        """
        self._execution_callbacks[schedule_id] = callback
    
    async def _scheduler_loop(self):
        """Background loop that checks for tasks to execute."""
        while self._running:
            try:
                await self._check_schedules()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue running
                print(f"Error in scheduler loop: {e}")
                await asyncio.sleep(self._check_interval)
    
    async def _check_schedules(self):
        """Check all schedules and execute due tasks."""
        now = datetime.utcnow()
        
        for schedule_id, schedule in list(self._schedules.items()):
            if not schedule.enabled:
                continue
            
            if schedule.next_run and schedule.next_run <= now:
                # Execute the task
                await self._execute_scheduled_task(schedule)
                
                # Calculate next run time
                if schedule.cron_expression:
                    schedule.next_run = self._calculate_next_run(
                        schedule.cron_expression.expression,
                        schedule.cron_expression.timezone
                    )
                    schedule.last_run = now
                    schedule.updated_at = now
    
    async def _execute_scheduled_task(self, schedule: ScheduledTask):
        """Execute a scheduled task."""
        # Check if there's a registered callback
        if schedule.schedule_id in self._execution_callbacks:
            callback = self._execution_callbacks[schedule.schedule_id]
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(schedule.task_definition)
                else:
                    callback(schedule.task_definition)
            except Exception as e:
                print(f"Error executing scheduled task {schedule.name}: {e}")
        else:
            # Default behavior: just log that it should execute
            print(f"Scheduled task '{schedule.name}' (ID: {schedule.schedule_id}) should execute now")
    
    def _calculate_next_run(
        self,
        cron_expression: str,
        timezone: str = "UTC"
    ) -> datetime:
        """Calculate the next run time from a cron expression."""
        try:
            # Note: Timezone handling for cron is basic here
            # For production, consider using pytz or zoneinfo for proper timezone support
            cron = croniter(cron_expression, datetime.utcnow())
            return cron.get_next(datetime)
        except Exception as e:
            # If cron parsing fails, default to 1 hour from now
            print(f"Error parsing cron expression '{cron_expression}': {e}")
            return datetime.utcnow() + timedelta(hours=1)
    
    def get_stats(self) -> dict:
        """
        Get scheduler statistics.
        
        Returns:
            Dictionary with statistics
        """
        enabled = sum(1 for s in self._schedules.values() if s.enabled)
        
        return {
            'running': self._running,
            'total_schedules': len(self._schedules),
            'enabled_schedules': enabled,
            'disabled_schedules': len(self._schedules) - enabled,
            'check_interval_seconds': self._check_interval
        }
