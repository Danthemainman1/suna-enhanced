"""
Communication Bus - Inter-agent communication system

Enables agents to communicate with each other through pub/sub messaging,
facilitating collaboration and coordination.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a message between agents"""
    id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommunicationBus:
    """
    Pub/Sub communication bus for inter-agent messaging.
    
    Features:
    - Topic-based messaging
    - Broadcast and direct messaging
    - Message queuing
    - Subscription management
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[Message] = []
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the communication bus"""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._message_worker())
        logger.info("Communication bus started")

    async def stop(self):
        """Stop the communication bus"""
        if not self._running:
            return

        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Communication bus stopped")

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.debug(f"Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str, callback: Callable):
        """Unsubscribe from a topic"""
        if topic in self.subscribers:
            self.subscribers[topic].remove(callback)
            if not self.subscribers[topic]:
                del self.subscribers[topic]
        logger.debug(f"Unsubscribed from topic: {topic}")

    async def publish(
        self,
        from_agent: str,
        topic: str,
        payload: Dict[str, Any],
        to_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Publish a message to a topic.
        
        Args:
            from_agent: ID of the sending agent
            topic: Topic name
            payload: Message payload
            to_agent: Optional recipient agent ID (for direct messaging)
            metadata: Optional metadata
            
        Returns:
            The published message
        """
        message = Message(
            id=f"msg_{int(datetime.utcnow().timestamp() * 1000)}",
            from_agent=from_agent,
            to_agent=to_agent,
            topic=topic,
            payload=payload,
            metadata=metadata or {},
        )

        await self.message_queue.put(message)
        self.message_history.append(message)

        logger.debug(
            f"Published message from {from_agent} to topic {topic}"
            + (f" (direct to {to_agent})" if to_agent else " (broadcast)")
        )

        return message

    async def _message_worker(self):
        """Worker that processes messages from the queue"""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )

                # Deliver to subscribers
                if message.topic in self.subscribers:
                    for callback in self.subscribers[message.topic]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(message)
                            else:
                                callback(message)
                        except Exception as e:
                            logger.error(
                                f"Error in message callback: {e}", exc_info=True
                            )

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message worker: {e}", exc_info=True)

    def get_message_history(
        self, topic: Optional[str] = None, limit: int = 100
    ) -> List[Message]:
        """Get message history, optionally filtered by topic"""
        messages = self.message_history
        if topic:
            messages = [m for m in messages if m.topic == topic]
        return messages[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get communication bus statistics"""
        return {
            "total_messages": len(self.message_history),
            "topics": len(self.subscribers),
            "queued_messages": self.message_queue.qsize(),
            "running": self._running,
        }
