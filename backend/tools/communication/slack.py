"""
Slack integration tool.

Provides comprehensive Slack API integration with OAuth2 and bot token support.
"""

import asyncio
import httpx
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError, ToolRateLimitError


logger = logging.getLogger(__name__)


class SlackTool(BaseTool):
    """
    Slack API integration tool.
    
    Supports:
    - Message sending (channels, DMs, threads)
    - File uploads
    - Channel and user management
    - Reactions
    - OAuth2 and Bot token authentication
    """
    
    name = "slack"
    description = "Send messages, upload files, and manage Slack workspaces"
    version = "1.0.0"
    category = ToolCategory.COMMUNICATION.value
    
    def __init__(self, **config):
        """
        Initialize Slack tool.
        
        Args:
            token: Slack bot token (required)
            oauth_token: OAuth2 token (optional)
            base_url: Slack API base URL (default: https://slack.com/api)
        """
        super().__init__(**config)
        self.token = config.get("token")
        self.oauth_token = config.get("oauth_token")
        self.base_url = config.get("base_url", "https://slack.com/api")
        
        if not self.token and not self.oauth_token:
            raise ToolAuthenticationError(
                "Slack token or oauth_token required",
                tool_name=self.name
            )
    
    def get_capabilities(self) -> List[str]:
        """Get Slack tool capabilities."""
        return [
            "messaging",
            "file_upload",
            "channel_management",
            "user_management",
            "reactions",
            "threads",
        ]
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get Slack tool parameters."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=[
                    "send_message",
                    "send_dm",
                    "upload_file",
                    "list_channels",
                    "list_users",
                    "add_reaction",
                    "reply_thread",
                    "create_channel",
                ]
            ),
            ToolParameter(
                name="channel",
                type="string",
                description="Channel ID or name",
                required=False
            ),
            ToolParameter(
                name="user_id",
                type="string",
                description="User ID for DMs",
                required=False
            ),
            ToolParameter(
                name="text",
                type="string",
                description="Message text",
                required=False
            ),
            ToolParameter(
                name="blocks",
                type="array",
                description="Slack Block Kit blocks",
                required=False
            ),
            ToolParameter(
                name="thread_ts",
                type="string",
                description="Thread timestamp for replies",
                required=False
            ),
        ]
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Slack API with retries.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            retries: Number of retries
            
        Returns:
            Response JSON
            
        Raises:
            ToolRateLimitError: If rate limited
            ToolExecutionError: If request fails
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token or self.oauth_token}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers, params=data)
                    else:
                        response = await client.post(url, headers=headers, json=data)
                    
                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        if attempt < retries - 1:
                            logger.warning(f"Rate limited, retrying after {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        raise ToolRateLimitError(
                            f"Rate limited by Slack API",
                            tool_name=self.name,
                            retry_after=retry_after
                        )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # Check Slack API error
                    if not result.get("ok"):
                        error = result.get("error", "Unknown error")
                        raise ToolExecutionError(
                            f"Slack API error: {error}",
                            tool_name=self.name,
                            metadata={"response": result}
                        )
                    
                    return result
                    
            except httpx.HTTPError as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
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
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None
    ) -> ToolResult:
        """Send a message to a Slack channel."""
        data = {
            "channel": channel,
            "text": text,
        }
        
        if blocks:
            data["blocks"] = blocks
        if thread_ts:
            data["thread_ts"] = thread_ts
        
        result = await self._make_request("POST", "chat.postMessage", data)
        
        return ToolResult.success_result(
            output={
                "message_ts": result.get("ts"),
                "channel": result.get("channel"),
            },
            tool_name=self.name,
            metadata={"action": "send_message"}
        )
    
    async def send_dm(self, user_id: str, text: str) -> ToolResult:
        """Send a direct message to a user."""
        # Open DM channel first
        dm_result = await self._make_request(
            "POST",
            "conversations.open",
            {"users": user_id}
        )
        
        channel_id = dm_result.get("channel", {}).get("id")
        
        # Send message
        return await self.send_message(channel_id, text)
    
    async def upload_file(
        self,
        channel: str,
        file_content: bytes,
        filename: str,
        title: Optional[str] = None
    ) -> ToolResult:
        """Upload a file to Slack."""
        # Note: This is simplified. Full implementation would use files.upload
        data = {
            "channels": channel,
            "filename": filename,
            "title": title or filename,
        }
        
        # For production, implement proper multipart file upload
        result = await self._make_request("POST", "files.upload", data)
        
        return ToolResult.success_result(
            output={"file_id": result.get("file", {}).get("id")},
            tool_name=self.name,
            metadata={"action": "upload_file"}
        )
    
    async def list_channels(self) -> ToolResult:
        """List all channels in the workspace."""
        result = await self._make_request("GET", "conversations.list")
        
        channels = result.get("channels", [])
        channel_list = [
            {"id": ch.get("id"), "name": ch.get("name")}
            for ch in channels
        ]
        
        return ToolResult.success_result(
            output=channel_list,
            tool_name=self.name,
            metadata={"action": "list_channels", "count": len(channel_list)}
        )
    
    async def list_users(self) -> ToolResult:
        """List all users in the workspace."""
        result = await self._make_request("GET", "users.list")
        
        users = result.get("members", [])
        user_list = [
            {
                "id": user.get("id"),
                "name": user.get("name"),
                "real_name": user.get("real_name"),
            }
            for user in users
        ]
        
        return ToolResult.success_result(
            output=user_list,
            tool_name=self.name,
            metadata={"action": "list_users", "count": len(user_list)}
        )
    
    async def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> ToolResult:
        """Add a reaction to a message."""
        data = {
            "channel": channel,
            "timestamp": timestamp,
            "name": emoji.strip(":")  # Remove colons if present
        }
        
        await self._make_request("POST", "reactions.add", data)
        
        return ToolResult.success_result(
            output={"emoji": emoji, "added": True},
            tool_name=self.name,
            metadata={"action": "add_reaction"}
        )
    
    async def reply_thread(
        self,
        channel: str,
        thread_ts: str,
        text: str
    ) -> ToolResult:
        """Reply to a thread."""
        return await self.send_message(channel, text, thread_ts=thread_ts)
    
    async def create_channel(
        self,
        name: str,
        is_private: bool = False
    ) -> ToolResult:
        """Create a new channel."""
        data = {
            "name": name,
            "is_private": is_private
        }
        
        result = await self._make_request("POST", "conversations.create", data)
        
        return ToolResult.success_result(
            output={"channel_id": result.get("channel", {}).get("id")},
            tool_name=self.name,
            metadata={"action": "create_channel"}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute Slack action."""
        action = kwargs.get("action")
        
        if action == "send_message":
            return await self.send_message(
                channel=kwargs.get("channel"),
                text=kwargs.get("text"),
                blocks=kwargs.get("blocks"),
                thread_ts=kwargs.get("thread_ts")
            )
        
        elif action == "send_dm":
            return await self.send_dm(
                user_id=kwargs.get("user_id"),
                text=kwargs.get("text")
            )
        
        elif action == "upload_file":
            return await self.upload_file(
                channel=kwargs.get("channel"),
                file_content=kwargs.get("file_content"),
                filename=kwargs.get("filename"),
                title=kwargs.get("title")
            )
        
        elif action == "list_channels":
            return await self.list_channels()
        
        elif action == "list_users":
            return await self.list_users()
        
        elif action == "add_reaction":
            return await self.add_reaction(
                channel=kwargs.get("channel"),
                timestamp=kwargs.get("timestamp"),
                emoji=kwargs.get("emoji")
            )
        
        elif action == "reply_thread":
            return await self.reply_thread(
                channel=kwargs.get("channel"),
                thread_ts=kwargs.get("thread_ts"),
                text=kwargs.get("text")
            )
        
        elif action == "create_channel":
            return await self.create_channel(
                name=kwargs.get("name"),
                is_private=kwargs.get("is_private", False)
            )
        
        else:
            return ToolResult.error_result(
                error=f"Unknown action: {action}",
                tool_name=self.name
            )
