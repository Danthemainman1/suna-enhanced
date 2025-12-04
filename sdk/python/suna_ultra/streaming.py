"""Streaming support for Suna Ultra SDK using Server-Sent Events (SSE)."""

import json
from typing import Iterator, AsyncIterator
import httpx
from sseclient import SSEClient
from .models import TaskEvent
from .exceptions import SunaError


class StreamHandler:
    """Handles SSE streaming for task events."""
    
    @staticmethod
    def parse_sse_event(event_data: str) -> TaskEvent:
        """
        Parse an SSE event into a TaskEvent model.
        
        Args:
            event_data: Raw event data string
        
        Returns:
            Parsed TaskEvent
        """
        try:
            data = json.loads(event_data) if event_data else {}
            return TaskEvent(**data)
        except (json.JSONDecodeError, ValueError) as e:
            raise SunaError(f"Failed to parse SSE event: {e}")
    
    @staticmethod
    def stream_events(response: httpx.Response) -> Iterator[TaskEvent]:
        """
        Stream events from an SSE response (synchronous).
        
        Args:
            response: httpx Response object with SSE data
        
        Yields:
            TaskEvent objects
        """
        client = SSEClient(response)
        for event in client.events():
            if event.data:
                yield StreamHandler.parse_sse_event(event.data)
    
    @staticmethod
    async def stream_events_async(response: httpx.Response) -> AsyncIterator[TaskEvent]:
        """
        Stream events from an SSE response (asynchronous).
        
        Args:
            response: httpx Response object with SSE data
        
        Yields:
            TaskEvent objects
        """
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data:
                    yield StreamHandler.parse_sse_event(data)
