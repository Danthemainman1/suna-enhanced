"""
Twilio SMS integration tool.

Provides SMS and MMS messaging via Twilio API.
"""

import asyncio
import httpx
from typing import Optional, List, Dict, Any
import logging
import base64

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError


logger = logging.getLogger(__name__)


class TwilioSMSTool(BaseTool):
    """
    Twilio SMS/MMS integration.
    
    Supports:
    - SMS sending
    - MMS sending (with media)
    - Message retrieval
    """
    
    name = "twilio_sms"
    description = "Send SMS and MMS messages via Twilio"
    version = "1.0.0"
    category = ToolCategory.COMMUNICATION.value
    
    def __init__(self, **config):
        """
        Initialize Twilio tool.
        
        Args:
            account_sid: Twilio account SID (required)
            auth_token: Twilio auth token (required)
            from_number: Twilio phone number (required)
        """
        super().__init__(**config)
        self.account_sid = config.get("account_sid")
        self.auth_token = config.get("auth_token")
        self.from_number = config.get("from_number")
        self.base_url = "https://api.twilio.com/2010-04-01"
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ToolAuthenticationError(
                "Twilio credentials required (account_sid, auth_token, from_number)",
                tool_name=self.name
            )
    
    def get_capabilities(self) -> List[str]:
        """Get Twilio tool capabilities."""
        return ["sms", "mms", "message_retrieval"]
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get Twilio tool parameters."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=["send_sms", "send_mms", "get_messages"]
            ),
            ToolParameter(
                name="to",
                type="string",
                description="Recipient phone number",
                required=False
            ),
            ToolParameter(
                name="body",
                type="string",
                description="Message body",
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
        """Make authenticated request to Twilio API with retries."""
        url = f"{self.base_url}/{endpoint}"
        
        # Basic auth
        auth_str = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
        }
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers, params=data)
                    else:
                        response = await client.post(url, headers=headers, data=data)
                    
                    response.raise_for_status()
                    return response.json()
                    
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
    
    async def send_sms(self, to: str, body: str) -> ToolResult:
        """Send an SMS message."""
        data = {
            "From": self.from_number,
            "To": to,
            "Body": body
        }
        
        result = await self._make_request(
            "POST",
            f"Accounts/{self.account_sid}/Messages.json",
            data
        )
        
        return ToolResult.success_result(
            output={
                "message_sid": result.get("sid"),
                "status": result.get("status"),
                "to": to
            },
            tool_name=self.name,
            metadata={"action": "send_sms"}
        )
    
    async def send_mms(
        self,
        to: str,
        body: str,
        media_url: str
    ) -> ToolResult:
        """Send an MMS message with media."""
        data = {
            "From": self.from_number,
            "To": to,
            "Body": body,
            "MediaUrl": media_url
        }
        
        result = await self._make_request(
            "POST",
            f"Accounts/{self.account_sid}/Messages.json",
            data
        )
        
        return ToolResult.success_result(
            output={
                "message_sid": result.get("sid"),
                "status": result.get("status"),
                "to": to
            },
            tool_name=self.name,
            metadata={"action": "send_mms"}
        )
    
    async def get_messages(self, limit: int = 20) -> ToolResult:
        """Get recent messages."""
        result = await self._make_request(
            "GET",
            f"Accounts/{self.account_sid}/Messages.json",
            {"PageSize": limit}
        )
        
        messages = result.get("messages", [])
        
        return ToolResult.success_result(
            output=messages,
            tool_name=self.name,
            metadata={"action": "get_messages", "count": len(messages)}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute Twilio action."""
        action = kwargs.get("action")
        
        if action == "send_sms":
            return await self.send_sms(
                to=kwargs.get("to"),
                body=kwargs.get("body")
            )
        elif action == "send_mms":
            return await self.send_mms(
                to=kwargs.get("to"),
                body=kwargs.get("body"),
                media_url=kwargs.get("media_url")
            )
        elif action == "get_messages":
            return await self.get_messages(limit=kwargs.get("limit", 20))
        else:
            return ToolResult.error_result(
                error=f"Unknown action: {action}",
                tool_name=self.name
            )
