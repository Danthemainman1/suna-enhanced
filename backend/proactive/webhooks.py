"""
Webhook management for incoming webhook endpoints.

This module provides webhook endpoints that can trigger agents
when HTTP requests are received.
"""

import uuid
import hmac
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from core.services import redis
from core.utils.logger import logger
from .models import Webhook, WebhookEvent


class WebhookManager:
    """Manages incoming webhook endpoints."""
    
    def __init__(self):
        """Initialize the webhook manager."""
        self._webhooks: Dict[str, Webhook] = {}
        self._webhooks_by_path: Dict[str, str] = {}  # url_path -> webhook_id
        self._events: Dict[str, list[WebhookEvent]] = {}
    
    async def create(self, workspace_id: str, name: str, trigger_id: str) -> Webhook:
        """Create a new webhook endpoint.
        
        Args:
            workspace_id: Workspace this webhook belongs to
            name: Human-readable webhook name
            trigger_id: Trigger to fire when webhook is called
        
        Returns:
            Created Webhook object
        """
        webhook_id = str(uuid.uuid4())
        url_path = str(uuid.uuid4())  # Generate unique path
        secret = self._generate_secret()
        
        webhook = Webhook(
            id=webhook_id,
            workspace_id=workspace_id,
            name=name,
            url_path=url_path,
            secret=secret,
            trigger_id=trigger_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={}
        )
        
        self._webhooks[webhook_id] = webhook
        self._webhooks_by_path[url_path] = webhook_id
        self._events[webhook_id] = []
        
        # Store in Redis for persistence
        try:
            await self._save_webhook(webhook)
        except Exception as e:
            logger.error(f"Failed to save webhook to Redis: {e}")
        
        logger.info(f"Created webhook {webhook_id}: {name}")
        return webhook
    
    async def verify_signature(self, webhook_id: str, payload: bytes, signature: str) -> bool:
        """Verify webhook signature for security.
        
        Args:
            webhook_id: Webhook ID
            payload: Raw payload bytes
            signature: Signature from request header
        
        Returns:
            True if signature is valid, False otherwise
        """
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return False
        
        # Compute expected signature
        expected_signature = hmac.new(
            webhook.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
    
    async def process(self, url_path: str, payload: dict, headers: dict) -> str:
        """Process an incoming webhook request.
        
        Args:
            url_path: URL path from the request
            payload: Parsed payload data
            headers: Request headers
        
        Returns:
            Task ID of the triggered agent run
        
        Raises:
            ValueError: If webhook not found or inactive
        """
        webhook_id = self._webhooks_by_path.get(url_path)
        if not webhook_id:
            raise ValueError(f"Webhook not found for path: {url_path}")
        
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            raise ValueError(f"Webhook {webhook_id} not found")
        
        if not webhook.is_active:
            raise ValueError(f"Webhook {webhook_id} is not active")
        
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        try:
            # TODO: Implement actual trigger firing logic
            # For now, just simulate processing
            task_id = str(uuid.uuid4())
            
            event = WebhookEvent(
                id=event_id,
                webhook_id=webhook_id,
                timestamp=now,
                payload=payload,
                headers=headers,
                task_id=task_id,
                success=True,
                error=None
            )
            
            # Store event
            if webhook_id not in self._events:
                self._events[webhook_id] = []
            self._events[webhook_id].append(event)
            
            logger.info(f"Processed webhook {webhook_id}, started task {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error processing webhook {webhook_id}: {e}")
            
            event = WebhookEvent(
                id=event_id,
                webhook_id=webhook_id,
                timestamp=now,
                payload=payload,
                headers=headers,
                task_id=None,
                success=False,
                error=str(e)
            )
            self._events[webhook_id].append(event)
            
            raise
    
    async def list(self, workspace_id: str) -> List[Webhook]:
        """List all webhooks for a workspace.
        
        Args:
            workspace_id: Workspace ID to filter by
        
        Returns:
            List of Webhook objects
        """
        return [w for w in self._webhooks.values() if w.workspace_id == workspace_id]
    
    async def get(self, webhook_id: str) -> Optional[Webhook]:
        """Get a specific webhook by ID.
        
        Args:
            webhook_id: Webhook ID
        
        Returns:
            Webhook object or None if not found
        """
        return self._webhooks.get(webhook_id)
    
    async def delete(self, webhook_id: str) -> bool:
        """Delete a webhook.
        
        Args:
            webhook_id: Webhook ID
        
        Returns:
            True if deleted, False if not found
        """
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return False
        
        # Remove from path mapping
        if webhook.url_path in self._webhooks_by_path:
            del self._webhooks_by_path[webhook.url_path]
        
        del self._webhooks[webhook_id]
        if webhook_id in self._events:
            del self._events[webhook_id]
        
        # Delete from Redis
        try:
            await self._delete_webhook(webhook_id)
        except Exception as e:
            logger.error(f"Failed to delete webhook from Redis: {e}")
        
        logger.info(f"Deleted webhook {webhook_id}")
        return True
    
    async def regenerate_secret(self, webhook_id: str) -> Optional[Webhook]:
        """Regenerate webhook secret.
        
        Args:
            webhook_id: Webhook ID
        
        Returns:
            Updated Webhook object or None if not found
        """
        webhook = self._webhooks.get(webhook_id)
        if not webhook:
            return None
        
        webhook.secret = self._generate_secret()
        webhook.updated_at = datetime.utcnow()
        
        # Save to Redis
        try:
            await self._save_webhook(webhook)
        except Exception as e:
            logger.error(f"Failed to update webhook in Redis: {e}")
        
        logger.info(f"Regenerated secret for webhook {webhook_id}")
        return webhook
    
    def _generate_secret(self) -> str:
        """Generate a secure random secret for webhook signing."""
        return str(uuid.uuid4())
    
    async def _save_webhook(self, webhook: Webhook):
        """Save webhook to Redis."""
        if not redis.client:
            return
        
        key = f"proactive:webhook:{webhook.id}"
        await redis.client.set(
            key,
            webhook.model_dump_json(),
            ex=redis.REDIS_KEY_TTL
        )
        
        # Also save path mapping
        path_key = f"proactive:webhook:path:{webhook.url_path}"
        await redis.client.set(
            path_key,
            webhook.id,
            ex=redis.REDIS_KEY_TTL
        )
    
    async def _delete_webhook(self, webhook_id: str):
        """Delete webhook from Redis."""
        if not redis.client:
            return
        
        webhook = self._webhooks.get(webhook_id)
        if webhook:
            # Delete path mapping
            path_key = f"proactive:webhook:path:{webhook.url_path}"
            await redis.client.delete(path_key)
        
        key = f"proactive:webhook:{webhook_id}"
        await redis.client.delete(key)
