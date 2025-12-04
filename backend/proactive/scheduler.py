"""
Cron-based task scheduler for proactive agents.

This module provides scheduling functionality using cron expressions
to run agents at specific times.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from typing import List, Dict
from croniter import croniter
import pytz
from core.services import redis
from core.utils.logger import logger
from .models import ScheduledTask, ScheduledTaskRun


class Scheduler:
    """Manages scheduled tasks using cron expressions."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self._schedules: Dict[str, ScheduledTask] = {}
        self._runs: Dict[str, list[ScheduledTaskRun]] = {}
    
    async def create(
        self,
        name: str,
        workspace_id: str,
        agent_id: str,
        task_description: str,
        cron_expression: str,
        timezone: str = "UTC"
    ) -> ScheduledTask:
        """Create a new scheduled task.
        
        Args:
            name: Human-readable task name
            workspace_id: Workspace this schedule belongs to
            agent_id: Agent to run
            task_description: Task description to pass to agent
            cron_expression: Cron expression (e.g., "0 9 * * *" for 9am daily)
            timezone: Timezone for schedule (default: UTC)
        
        Returns:
            Created ScheduledTask object
        
        Raises:
            ValueError: If cron expression is invalid
        """
        # Validate cron expression
        try:
            tz = pytz.timezone(timezone)
            base_time = datetime.now(tz)
            cron = croniter(cron_expression, base_time)
            next_run = cron.get_next(datetime)
        except Exception as e:
            raise ValueError(f"Invalid cron expression or timezone: {e}")
        
        schedule_id = str(uuid.uuid4())
        
        schedule = ScheduledTask(
            id=schedule_id,
            name=name,
            workspace_id=workspace_id,
            agent_id=agent_id,
            task_description=task_description,
            cron_expression=cron_expression,
            timezone=timezone,
            is_active=True,
            next_run=next_run,
            last_run=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        self._schedules[schedule_id] = schedule
        self._runs[schedule_id] = []
        
        # Store in Redis for persistence
        try:
            await self._save_schedule(schedule)
        except Exception as e:
            logger.error(f"Failed to save schedule to Redis: {e}")
        
        logger.info(f"Created schedule {schedule_id}: {name}")
        return schedule
    
    async def list(self, workspace_id: str) -> List[ScheduledTask]:
        """List all schedules for a workspace.
        
        Args:
            workspace_id: Workspace ID to filter by
        
        Returns:
            List of ScheduledTask objects
        """
        return [s for s in self._schedules.values() if s.workspace_id == workspace_id]
    
    async def get(self, schedule_id: str) -> Optional[ScheduledTask]:
        """Get a specific schedule by ID.
        
        Args:
            schedule_id: Schedule ID
        
        Returns:
            ScheduledTask object or None if not found
        """
        return self._schedules.get(schedule_id)
    
    async def delete(self, schedule_id: str) -> bool:
        """Delete a schedule.
        
        Args:
            schedule_id: Schedule ID
        
        Returns:
            True if deleted, False if not found
        """
        if schedule_id not in self._schedules:
            return False
        
        del self._schedules[schedule_id]
        if schedule_id in self._runs:
            del self._runs[schedule_id]
        
        # Delete from Redis
        try:
            await self._delete_schedule(schedule_id)
        except Exception as e:
            logger.error(f"Failed to delete schedule from Redis: {e}")
        
        logger.info(f"Deleted schedule {schedule_id}")
        return True
    
    async def run_now(self, schedule_id: str) -> str:
        """Run a scheduled task immediately.
        
        Args:
            schedule_id: Schedule ID
        
        Returns:
            Task ID of the triggered agent run
        
        Raises:
            ValueError: If schedule not found
        """
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        return await self._execute_schedule(schedule)
    
    async def pause(self, schedule_id: str) -> Optional[ScheduledTask]:
        """Pause a schedule.
        
        Args:
            schedule_id: Schedule ID
        
        Returns:
            Updated ScheduledTask object or None if not found
        """
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None
        
        schedule.is_active = False
        schedule.updated_at = datetime.utcnow()
        
        # Save to Redis
        try:
            await self._save_schedule(schedule)
        except Exception as e:
            logger.error(f"Failed to update schedule in Redis: {e}")
        
        logger.info(f"Paused schedule {schedule_id}")
        return schedule
    
    async def resume(self, schedule_id: str) -> Optional[ScheduledTask]:
        """Resume a paused schedule.
        
        Args:
            schedule_id: Schedule ID
        
        Returns:
            Updated ScheduledTask object or None if not found
        """
        schedule = self._schedules.get(schedule_id)
        if not schedule:
            return None
        
        schedule.is_active = True
        schedule.updated_at = datetime.utcnow()
        
        # Recalculate next run time
        try:
            tz = pytz.timezone(schedule.timezone)
            base_time = datetime.now(tz)
            cron = croniter(schedule.cron_expression, base_time)
            schedule.next_run = cron.get_next(datetime)
        except Exception as e:
            logger.error(f"Failed to calculate next run time: {e}")
        
        # Save to Redis
        try:
            await self._save_schedule(schedule)
        except Exception as e:
            logger.error(f"Failed to update schedule in Redis: {e}")
        
        logger.info(f"Resumed schedule {schedule_id}")
        return schedule
    
    async def _execute_schedule(self, schedule: ScheduledTask) -> str:
        """Execute a scheduled task.
        
        Args:
            schedule: ScheduledTask to execute
        
        Returns:
            Task ID of the triggered agent run
        """
        run_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        try:
            # TODO: Implement actual agent triggering logic
            # For now, just simulate execution
            
            run = ScheduledTaskRun(
                id=run_id,
                schedule_id=schedule.id,
                timestamp=now,
                task_id=task_id,
                success=True,
                error=None
            )
            
            # Update schedule
            schedule.last_run = now
            
            # Calculate next run time
            try:
                tz = pytz.timezone(schedule.timezone)
                cron = croniter(schedule.cron_expression, now.replace(tzinfo=tz))
                schedule.next_run = cron.get_next(datetime)
            except Exception as e:
                logger.error(f"Failed to calculate next run time: {e}")
            
            # Store run record
            if schedule.id not in self._runs:
                self._runs[schedule.id] = []
            self._runs[schedule.id].append(run)
            
            # Save updated schedule
            await self._save_schedule(schedule)
            
            logger.info(f"Executed schedule {schedule.id}, started task {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error executing schedule {schedule.id}: {e}")
            
            run = ScheduledTaskRun(
                id=run_id,
                schedule_id=schedule.id,
                timestamp=now,
                task_id=None,
                success=False,
                error=str(e)
            )
            self._runs[schedule.id].append(run)
            
            raise
    
    async def _save_schedule(self, schedule: ScheduledTask):
        """Save schedule to Redis."""
        if not redis.client:
            return
        
        key = f"proactive:schedule:{schedule.id}"
        await redis.client.set(
            key,
            schedule.model_dump_json(),
            ex=redis.REDIS_KEY_TTL
        )
    
    async def _delete_schedule(self, schedule_id: str):
        """Delete schedule from Redis."""
        if not redis.client:
            return
        
        key = f"proactive:schedule:{schedule_id}"
        await redis.client.delete(key)
