"""
Trigger management for event-based agent firing.

This module provides trigger management for firing agents based on
various event types (webhooks, schedules, email, Slack, GitHub, etc.).
"""

import uuid
from datetime import datetime
from typing import Optional
from typing import List, Dict
from core.services import redis
from core.utils.logger import logger
from .models import Trigger, TriggerEvent, TriggerType


class TriggerManager:
    """Manages triggers that fire agents based on events."""
    
    def __init__(self):
        """Initialize the trigger manager."""
        self._triggers: Dict[str, Trigger] = {}
        self._events: Dict[str, list[TriggerEvent]] = {}
    
    async def create(
        self,
        name: str,
        workspace_id: str,
        trigger_type: TriggerType,
        config: dict,
        agent_id: str,
        task_template: str
    ) -> Trigger:
        """Create a new trigger.
        
        Args:
            name: Human-readable trigger name
            workspace_id: Workspace this trigger belongs to
            trigger_type: Type of trigger (webhook, schedule, etc.)
            config: Trigger-specific configuration
            agent_id: Agent to trigger
            task_template: Task description template with variables
        
        Returns:
            Created Trigger object
        """
        trigger_id = str(uuid.uuid4())
        
        trigger = Trigger(
            id=trigger_id,
            name=name,
            workspace_id=workspace_id,
            trigger_type=trigger_type,
            config=config,
            agent_id=agent_id,
            task_template=task_template,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        self._triggers[trigger_id] = trigger
        self._events[trigger_id] = []
        
        # Store in Redis for persistence
        try:
            await self._save_trigger(trigger)
        except Exception as e:
            logger.error(f"Failed to save trigger to Redis: {e}")
        
        logger.info(f"Created trigger {trigger_id}: {name}")
        return trigger
    
    async def fire(self, trigger_id: str, payload: dict) -> str:
        """Fire a trigger with the given payload.
        
        Args:
            trigger_id: Trigger ID to fire
            payload: Event payload data
        
        Returns:
            Task ID of the triggered agent run
        
        Raises:
            ValueError: If trigger not found or inactive
        """
        trigger = self._triggers.get(trigger_id)
        if not trigger:
            raise ValueError(f"Trigger {trigger_id} not found")
        
        if not trigger.is_active:
            raise ValueError(f"Trigger {trigger_id} is not active")
        
        event_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        try:
            # TODO: Implement actual agent triggering logic
            # For now, just simulate firing
            
            # Render task template with payload variables
            task_description = self._render_template(trigger.task_template, payload)
            
            # TODO: Actually start the agent with the task
            
            event = TriggerEvent(
                id=event_id,
                trigger_id=trigger_id,
                timestamp=now,
                payload=payload,
                task_id=task_id,
                success=True,
                error=None
            )
            
            # Store event
            if trigger_id not in self._events:
                self._events[trigger_id] = []
            self._events[trigger_id].append(event)
            
            logger.info(f"Fired trigger {trigger_id}, started task {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error firing trigger {trigger_id}: {e}")
            
            event = TriggerEvent(
                id=event_id,
                trigger_id=trigger_id,
                timestamp=now,
                payload=payload,
                task_id=None,
                success=False,
                error=str(e)
            )
            self._events[trigger_id].append(event)
            
            raise
    
    async def list(self, workspace_id: str) -> List[Trigger]:
        """List all triggers for a workspace.
        
        Args:
            workspace_id: Workspace ID to filter by
        
        Returns:
            List of Trigger objects
        """
        return [t for t in self._triggers.values() if t.workspace_id == workspace_id]
    
    async def get(self, trigger_id: str) -> Optional[Trigger]:
        """Get a specific trigger by ID.
        
        Args:
            trigger_id: Trigger ID
        
        Returns:
            Trigger object or None if not found
        """
        return self._triggers.get(trigger_id)
    
    async def delete(self, trigger_id: str) -> bool:
        """Delete a trigger.
        
        Args:
            trigger_id: Trigger ID
        
        Returns:
            True if deleted, False if not found
        """
        if trigger_id not in self._triggers:
            return False
        
        del self._triggers[trigger_id]
        if trigger_id in self._events:
            del self._events[trigger_id]
        
        # Delete from Redis
        try:
            await self._delete_trigger(trigger_id)
        except Exception as e:
            logger.error(f"Failed to delete trigger from Redis: {e}")
        
        logger.info(f"Deleted trigger {trigger_id}")
        return True
    
    def _render_template(self, template: str, payload: dict) -> str:
        """Render a task template with payload variables.
        
        Args:
            template: Task template string with {variable} placeholders
            payload: Dictionary of variable values
        
        Returns:
            Rendered task description
        """
        try:
            return template.format(**payload)
        except KeyError as e:
            logger.warning(f"Missing variable in template: {e}")
            return template
    
    async def _save_trigger(self, trigger: Trigger):
        """Save trigger to Redis."""
        if not redis.client:
            return
        
        key = f"proactive:trigger:{trigger.id}"
        await redis.client.set(
            key,
            trigger.model_dump_json(),
            ex=redis.REDIS_KEY_TTL
        )
    
    async def _delete_trigger(self, trigger_id: str):
        """Delete trigger from Redis."""
        if not redis.client:
            return
        
        key = f"proactive:trigger:{trigger_id}"
        await redis.client.delete(key)
