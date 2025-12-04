"""
Discord integration tool.

Provides Discord bot API integration for messaging and server management.
"""

import asyncio
import httpx
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError, ToolRateLimitError


logger = logging.getLogger(__name__)


class DiscordTool(BaseTool):
    """
    Discord bot API integration tool.
    
    Supports:
    - Message sending (channels, DMs)
    - Embed creation
    - File uploads
    - Server/guild management
    - Reactions
    """
    
    name = "discord"
    description = "Send messages, manage Discord servers, and interact with users"
    version = "1.0.0"
    category = ToolCategory.COMMUNICATION.value
    
    def __init__(self, **config):
        """
        Initialize Discord tool.
        
        Args:
            token: Discord bot token (required)
            base_url: Discord API base URL (default: https://discord.com/api/v10)
        """
        super().__init__(**config)
        self.token = config.get("token")
        self.base_url = config.get("base_url", "https://discord.com/api/v10")
        
        if not self.token:
            raise ToolAuthenticationError(
                "Discord bot token required",
                tool_name=self.name
            )
    
    def get_capabilities(self) -> List[str]:
        """Get Discord tool capabilities."""
        return [
            "messaging",
            "embeds",
            "file_upload",
            "guild_management",
            "reactions",
        ]
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get Discord tool parameters."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=[
                    "send_message",
                    "send_dm",
                    "create_embed",
                    "upload_file",
                    "list_guilds",
                    "list_channels",
                    "add_reaction",
                ]
            ),
            ToolParameter(
                name="channel_id",
                type="string",
                description="Channel ID",
                required=False
            ),
            ToolParameter(
                name="user_id",
                type="string",
                description="User ID for DMs",
                required=False
            ),
            ToolParameter(
                name="content",
                type="string",
                description="Message content",
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
        """Make authenticated request to Discord API with retries."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    elif method.upper() == "PATCH":
                        response = await client.patch(url, headers=headers, json=data)
                    else:
                        response = await client.delete(url, headers=headers)
                    
                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after = response.json().get("retry_after", 1)
                        if attempt < retries - 1:
                            logger.warning(f"Rate limited, retrying after {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        raise ToolRateLimitError(
                            f"Rate limited by Discord API",
                            tool_name=self.name,
                            retry_after=int(retry_after)
                        )
                    
                    response.raise_for_status()
                    return response.json() if response.content else {}
                    
            except httpx.HTTPError as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
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
        channel_id: str,
        content: str,
        embeds: Optional[List[Dict]] = None
    ) -> ToolResult:
        """Send a message to a Discord channel."""
        data = {"content": content}
        
        if embeds:
            data["embeds"] = embeds
        
        result = await self._make_request(
            "POST",
            f"channels/{channel_id}/messages",
            data
        )
        
        return ToolResult.success_result(
            output={
                "message_id": result.get("id"),
                "channel_id": result.get("channel_id"),
            },
            tool_name=self.name,
            metadata={"action": "send_message"}
        )
    
    async def send_dm(self, user_id: str, content: str) -> ToolResult:
        """Send a direct message to a user."""
        # Create DM channel
        dm_result = await self._make_request(
            "POST",
            "users/@me/channels",
            {"recipient_id": user_id}
        )
        
        channel_id = dm_result.get("id")
        
        # Send message
        return await self.send_message(channel_id, content)
    
    async def create_embed(
        self,
        title: str,
        description: str,
        fields: Optional[List[Dict[str, str]]] = None,
        color: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a Discord embed object."""
        embed = {
            "title": title,
            "description": description,
        }
        
        if fields:
            embed["fields"] = fields
        if color:
            embed["color"] = color
        
        return embed
    
    async def list_guilds(self) -> ToolResult:
        """List all guilds the bot is in."""
        result = await self._make_request("GET", "users/@me/guilds")
        
        guilds = [
            {"id": guild.get("id"), "name": guild.get("name")}
            for guild in result
        ]
        
        return ToolResult.success_result(
            output=guilds,
            tool_name=self.name,
            metadata={"action": "list_guilds", "count": len(guilds)}
        )
    
    async def list_channels(self, guild_id: str) -> ToolResult:
        """List all channels in a guild."""
        result = await self._make_request("GET", f"guilds/{guild_id}/channels")
        
        channels = [
            {
                "id": ch.get("id"),
                "name": ch.get("name"),
                "type": ch.get("type"),
            }
            for ch in result
        ]
        
        return ToolResult.success_result(
            output=channels,
            tool_name=self.name,
            metadata={"action": "list_channels", "count": len(channels)}
        )
    
    async def add_reaction(
        self,
        channel_id: str,
        message_id: str,
        emoji: str
    ) -> ToolResult:
        """Add a reaction to a message."""
        await self._make_request(
            "PUT",
            f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"
        )
        
        return ToolResult.success_result(
            output={"emoji": emoji, "added": True},
            tool_name=self.name,
            metadata={"action": "add_reaction"}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute Discord action."""
        action = kwargs.get("action")
        
        if action == "send_message":
            return await self.send_message(
                channel_id=kwargs.get("channel_id"),
                content=kwargs.get("content"),
                embeds=kwargs.get("embeds")
            )
        
        elif action == "send_dm":
            return await self.send_dm(
                user_id=kwargs.get("user_id"),
                content=kwargs.get("content")
            )
        
        elif action == "create_embed":
            embed = await self.create_embed(
                title=kwargs.get("title"),
                description=kwargs.get("description"),
                fields=kwargs.get("fields"),
                color=kwargs.get("color")
            )
            return ToolResult.success_result(
                output=embed,
                tool_name=self.name,
                metadata={"action": "create_embed"}
            )
        
        elif action == "list_guilds":
            return await self.list_guilds()
        
        elif action == "list_channels":
            return await self.list_channels(kwargs.get("guild_id"))
        
        elif action == "add_reaction":
            return await self.add_reaction(
                channel_id=kwargs.get("channel_id"),
                message_id=kwargs.get("message_id"),
                emoji=kwargs.get("emoji")
            )
        
        else:
            return ToolResult.error_result(
                error=f"Unknown action: {action}",
                tool_name=self.name
            )
