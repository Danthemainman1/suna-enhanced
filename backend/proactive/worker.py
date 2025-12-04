"""
Background worker for proactive agent system.

This module provides a background worker that:
1. Runs monitor checks at their intervals
2. Processes scheduled tasks at their cron times
3. Uses Redis for coordination
"""

import asyncio
import time
from datetime import datetime
from typing import Set
from core.services import redis
from core.utils.logger import logger

from .monitor import ProactiveMonitor
from .scheduler import Scheduler


class ProactiveWorker:
    """Background worker for proactive monitoring and scheduling."""
    
    def __init__(self):
        """Initialize the worker."""
        self.monitor_manager = ProactiveMonitor()
        self.scheduler = Scheduler()
        self.running = False
        self._tasks: Set[asyncio.Task] = set()
    
    async def start(self):
        """Start the background worker."""
        if self.running:
            logger.warning("Proactive worker already running")
            return
        
        self.running = True
        logger.info("Starting proactive worker")
        
        # Start monitor check loop
        monitor_task = asyncio.create_task(self._monitor_loop())
        self._tasks.add(monitor_task)
        monitor_task.add_done_callback(self._tasks.discard)
        
        # Start scheduler check loop
        scheduler_task = asyncio.create_task(self._scheduler_loop())
        self._tasks.add(scheduler_task)
        scheduler_task.add_done_callback(self._tasks.discard)
        
        logger.info("Proactive worker started")
    
    async def stop(self):
        """Stop the background worker."""
        if not self.running:
            return
        
        logger.info("Stopping proactive worker")
        self.running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        logger.info("Proactive worker stopped")
    
    async def _monitor_loop(self):
        """Main loop for checking monitors."""
        logger.info("Monitor check loop started")
        
        try:
            while self.running:
                try:
                    await self._check_monitors()
                except Exception as e:
                    logger.error(f"Error in monitor check loop: {e}")
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(10)  # Check every 10 seconds
        
        except asyncio.CancelledError:
            logger.info("Monitor check loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in monitor check loop: {e}")
    
    async def _check_monitors(self):
        """Check all active monitors and trigger if needed."""
        now = datetime.utcnow()
        
        # Get all monitors from all workspaces
        # In production, this should be paginated or fetched from database
        all_monitors = []
        for monitor in self.monitor_manager._monitors.values():
            if not monitor.is_active:
                continue
            
            # Check if it's time to run this monitor
            if monitor.last_check:
                seconds_since_check = (now - monitor.last_check).total_seconds()
                if seconds_since_check < monitor.check_interval:
                    continue
            
            all_monitors.append(monitor)
        
        # Check monitors
        if all_monitors:
            logger.debug(f"Checking {len(all_monitors)} monitors")
            
            for monitor in all_monitors:
                try:
                    await self.monitor_manager._check_monitor(monitor)
                except Exception as e:
                    logger.error(f"Error checking monitor {monitor.id}: {e}")
    
    async def _scheduler_loop(self):
        """Main loop for checking scheduled tasks."""
        logger.info("Scheduler check loop started")
        
        try:
            while self.running:
                try:
                    await self._check_schedules()
                except Exception as e:
                    logger.error(f"Error in scheduler check loop: {e}")
                
                # Sleep for a minute before checking again
                await asyncio.sleep(60)  # Check every minute
        
        except asyncio.CancelledError:
            logger.info("Scheduler check loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in scheduler check loop: {e}")
    
    async def _check_schedules(self):
        """Check all active schedules and run if needed."""
        now = datetime.utcnow()
        
        # Get all schedules from all workspaces
        all_schedules = []
        for schedule in self.scheduler._schedules.values():
            if not schedule.is_active:
                continue
            
            # Check if it's time to run this schedule
            if schedule.next_run and schedule.next_run <= now:
                all_schedules.append(schedule)
        
        # Execute schedules
        if all_schedules:
            logger.debug(f"Executing {len(all_schedules)} scheduled tasks")
            
            for schedule in all_schedules:
                try:
                    await self.scheduler._execute_schedule(schedule)
                except Exception as e:
                    logger.error(f"Error executing schedule {schedule.id}: {e}")


# Global worker instance
_worker: ProactiveWorker = None


async def initialize():
    """Initialize and start the proactive worker."""
    global _worker
    
    if _worker is not None:
        logger.warning("Proactive worker already initialized")
        return
    
    _worker = ProactiveWorker()
    await _worker.start()
    logger.info("Proactive worker initialized")


async def cleanup():
    """Stop and cleanup the proactive worker."""
    global _worker
    
    if _worker is None:
        return
    
    await _worker.stop()
    _worker = None
    logger.info("Proactive worker cleaned up")


def get_worker() -> ProactiveWorker:
    """Get the global worker instance."""
    return _worker
