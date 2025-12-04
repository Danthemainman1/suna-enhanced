"""
Telegram Bot API integration tool.

Provides Telegram bot functionality for messaging and interactions.
"""

import asyncio
import httpx
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError


logger = logging.getLogger(__name__)


class TelegramTool(BaseTool):
    """
    Telegram Bot API integration.
    
    Supports:
    - Message sending (text, photos, documents)
    - Keyboard creation
    - Update retrieval
    - Callback handling
    """
    
    name = "telegram"
    description = "Send messages and interact with Telegram users"
    version = "1.0.0"
    category = ToolCategory.COMMUNICATION.value
    
    def __init__(self, **config):
        """
        Initialize Telegram tool.
        
        Args:
            token: Telegram bot API token (required)
            base_url: Telegram API base URL
        """
        super().__init__(**config)
        self.token = config.get("token")
        self.base_url = config.get("base_url", "https://api.telegram.org")
        
        if not self.token:
            raise ToolAuthenticationError(
                "Telegram bot token required",
                tool_name=self.name
            )
    
    def get_capabilities(self) -> List[str]:
        """Get Telegram tool capabilities."""
        return ["messaging", "file_upload", "keyboards", "callbacks"]
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get Telegram tool parameters."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=[
                    "send_message",
                    "send_photo",
                    "send_document",
                    "send_keyboard",
                    "get_updates",
                ]
            ),
            ToolParameter(
                name="chat_id",
                type="string",
                description="Chat ID",
                required=False
            ),
            ToolParameter(
                name="text",
                type="string",
                description="Message text",
                required=False
            ),
        ]
    
    async def _make_request(
        self,
        method: str,
        data: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """Make request to Telegram API with retries."""
        url = f"{self.base_url}/bot{self.token}/{method}"
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=data)
                    response.raise_for_status()
                    result = response.json()
                    
                    if not result.get("ok"):
                        raise ToolExecutionError(
                            f"Telegram API error: {result.get('description')}",
                            tool_name=self.name
                        )
                    
                    return result.get("result", {})
                    
            except httpx.HTTPError as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                raise ToolExecutionError(
                    f"HTTP request failed: {str(e)}",
                    tool_name=self.name
                )
        
        raise ToolExecutionError(
            f"Request failed after {retries} retries",
            tool_name=self.name
        )
    
    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = None
    ) -> ToolResult:
        """Send a text message."""
        data = {"chat_id": chat_id, "text": text}
        
        if parse_mode:
            data["parse_mode"] = parse_mode
        
        result = await self._make_request("sendMessage", data)
        
        return ToolResult.success_result(
            output={"message_id": result.get("message_id")},
            tool_name=self.name,
            metadata={"action": "send_message"}
        )
    
    async def send_photo(self, chat_id: str, photo: str) -> ToolResult:
        """Send a photo."""
        data = {"chat_id": chat_id, "photo": photo}
        result = await self._make_request("sendPhoto", data)
        
        return ToolResult.success_result(
            output={"message_id": result.get("message_id")},
            tool_name=self.name,
            metadata={"action": "send_photo"}
        )
    
    async def send_document(self, chat_id: str, document: str) -> ToolResult:
        """Send a document."""
        data = {"chat_id": chat_id, "document": document}
        result = await self._make_request("sendDocument", data)
        
        return ToolResult.success_result(
            output={"message_id": result.get("message_id")},
            tool_name=self.name,
            metadata={"action": "send_document"}
        )
    
    async def get_updates(self, offset: Optional[int] = None) -> ToolResult:
        """Get updates from Telegram."""
        data = {}
        if offset:
            data["offset"] = offset
        
        result = await self._make_request("getUpdates", data)
        
        return ToolResult.success_result(
            output=result,
            tool_name=self.name,
            metadata={"action": "get_updates", "count": len(result)}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute Telegram action."""
        action = kwargs.get("action")
        
        if action == "send_message":
            return await self.send_message(
                chat_id=kwargs.get("chat_id"),
                text=kwargs.get("text"),
                parse_mode=kwargs.get("parse_mode")
            )
        elif action == "send_photo":
            return await self.send_photo(
                chat_id=kwargs.get("chat_id"),
                photo=kwargs.get("photo")
            )
        elif action == "send_document":
            return await self.send_document(
                chat_id=kwargs.get("chat_id"),
                document=kwargs.get("document")
            )
        elif action == "get_updates":
            return await self.get_updates(offset=kwargs.get("offset"))
        else:
            return ToolResult.error_result(
                error=f"Unknown action: {action}",
                tool_name=self.name
            )
