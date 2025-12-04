"""
Proactive monitor implementation for continuous condition checking.

This module provides monitors that continuously check conditions and trigger
agents when conditions are met.
"""

import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from typing import Optional
from core.services import redis
from core.utils.logger import logger
from .models import Monitor, MonitorEvent


class ProactiveMonitor:
    """Manages proactive monitors that check conditions and trigger agents."""
    
    def __init__(self):
        """Initialize the monitor manager."""
        self._monitors: Dict[str, Monitor] = {}
        self._events: Dict[str, list[MonitorEvent]] = {}
    
    async def create(
        self,
        name: str,
        agent_id: str,
        workspace_id: str,
        condition: str,
        action: str,
        check_interval: int = 300
    ) -> Monitor:
        """Create a new monitor.
        
        Args:
            name: Human-readable monitor name
            agent_id: Agent to trigger when condition met
            workspace_id: Workspace this monitor belongs to
            condition: Condition to monitor (natural language or expression)
            action: Action agent should perform when triggered
            check_interval: Seconds between condition checks (default: 300)
        
        Returns:
            Created Monitor object
        """
        monitor_id = str(uuid.uuid4())
        
        monitor = Monitor(
            id=monitor_id,
            name=name,
            agent_id=agent_id,
            workspace_id=workspace_id,
            condition=condition,
            action=action,
            check_interval=check_interval,
            is_active=True,
            last_check=None,
            last_triggered=None,
            trigger_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        self._monitors[monitor_id] = monitor
        self._events[monitor_id] = []
        
        # Store in Redis for persistence
        try:
            await self._save_monitor(monitor)
        except Exception as e:
            logger.error(f"Failed to save monitor to Redis: {e}")
        
        logger.info(f"Created monitor {monitor_id}: {name}")
        return monitor
    
    async def list(self, workspace_id: str) -> List[Monitor]:
        """List all monitors for a workspace.
        
        Args:
            workspace_id: Workspace ID to filter by
        
        Returns:
            List of Monitor objects
        """
        return [m for m in self._monitors.values() if m.workspace_id == workspace_id]
    
    async def get(self, monitor_id: str) -> Optional[Monitor]:
        """Get a specific monitor by ID.
        
        Args:
            monitor_id: Monitor ID
        
        Returns:
            Monitor object or None if not found
        """
        return self._monitors.get(monitor_id)
    
    async def update(self, monitor_id: str, **kwargs) -> Optional[Monitor]:
        """Update a monitor.
        
        Args:
            monitor_id: Monitor ID
            **kwargs: Fields to update
        
        Returns:
            Updated Monitor object or None if not found
        """
        monitor = self._monitors.get(monitor_id)
        if not monitor:
            return None
        
        # Update allowed fields
        allowed_fields = {"name", "condition", "action", "check_interval", "is_active"}
        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(monitor, key):
                setattr(monitor, key, value)
        
        monitor.updated_at = datetime.utcnow()
        
        # Save to Redis
        try:
            await self._save_monitor(monitor)
        except Exception as e:
            logger.error(f"Failed to update monitor in Redis: {e}")
        
        logger.info(f"Updated monitor {monitor_id}")
        return monitor
    
    async def delete(self, monitor_id: str) -> bool:
        """Delete a monitor.
        
        Args:
            monitor_id: Monitor ID
        
        Returns:
            True if deleted, False if not found
        """
        if monitor_id not in self._monitors:
            return False
        
        del self._monitors[monitor_id]
        if monitor_id in self._events:
            del self._events[monitor_id]
        
        # Delete from Redis
        try:
            await self._delete_monitor(monitor_id)
        except Exception as e:
            logger.error(f"Failed to delete monitor from Redis: {e}")
        
        logger.info(f"Deleted monitor {monitor_id}")
        return True
    
    async def pause(self, monitor_id: str) -> Optional[Monitor]:
        """Pause a monitor.
        
        Args:
            monitor_id: Monitor ID
        
        Returns:
            Updated Monitor object or None if not found
        """
        return await self.update(monitor_id, is_active=False)
    
    async def resume(self, monitor_id: str) -> Optional[Monitor]:
        """Resume a monitor.
        
        Args:
            monitor_id: Monitor ID
        
        Returns:
            Updated Monitor object or None if not found
        """
        return await self.update(monitor_id, is_active=True)
    
    async def get_history(self, monitor_id: str, limit: int = 100) -> List[MonitorEvent]:
        """Get monitor event history.
        
        Args:
            monitor_id: Monitor ID
            limit: Maximum number of events to return
        
        Returns:
            List of MonitorEvent objects
        """
        events = self._events.get(monitor_id, [])
        return events[-limit:]
    
    async def check_now(self, monitor_id: str) -> Optional[MonitorEvent]:
        """Manually trigger a monitor check now.
        
        Args:
            monitor_id: Monitor ID
        
        Returns:
            MonitorEvent object or None if monitor not found
        """
        monitor = self._monitors.get(monitor_id)
        if not monitor:
            return None
        
        return await self._check_monitor(monitor)
    
    async def _check_monitor(self, monitor: Monitor) -> MonitorEvent:
        """Check a monitor\'s condition and trigger if met.
        
        Args:
            monitor: Monitor to check
        
        Returns:
            MonitorEvent with check results
        """
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        try:
            # TODO: Implement actual condition checking logic
            # For now, just simulate a check
            condition_met = False
            triggered = False
            task_id = None
            error = None
            
            # Update monitor
            monitor.last_check = now
            if condition_met:
                # TODO: Actually trigger the agent
                triggered = True
                monitor.last_triggered = now
                monitor.trigger_count += 1
                task_id = str(uuid.uuid4())
            
            event = MonitorEvent(
                id=event_id,
                monitor_id=monitor.id,
                timestamp=now,
                condition_met=condition_met,
                triggered=triggered,
                task_id=task_id,
                result_data={},
                error=error
            )
            
            # Store event
            if monitor.id not in self._events:
                self._events[monitor.id] = []
            self._events[monitor.id].append(event)
            
            # Update monitor in storage
            await self._save_monitor(monitor)
            
            return event
            
        except Exception as e:
            logger.error(f"Error checking monitor {monitor.id}: {e}")
            event = MonitorEvent(
                id=event_id,
                monitor_id=monitor.id,
                timestamp=now,
                condition_met=False,
                triggered=False,
                task_id=None,
                result_data={},
                error=str(e)
            )
            return event
    
    async def _save_monitor(self, monitor: Monitor):
        """Save monitor to Redis."""
        if not redis.client:
            return
        
        key = f"proactive:monitor:{monitor.id}"
        await redis.client.set(
            key,
            monitor.model_dump_json(),
            ex=redis.REDIS_KEY_TTL
        )
    
    async def _delete_monitor(self, monitor_id: str):
        """Delete monitor from Redis."""
        if not redis.client:
            return
        
        key = f"proactive:monitor:{monitor_id}"
        await redis.client.delete(key)
