"""Tool operations for Suna Ultra SDK."""

from typing import List, Optional, Any
import httpx
from .models import Tool, ToolResult
from .exceptions import NotFoundError, SunaError


class ToolOperations:
    """Handles tool-related operations."""
    
    def __init__(self, client: httpx.Client, base_url: str):
        """
        Initialize tool operations.
        
        Args:
            client: httpx Client instance
            base_url: Base URL for API requests
        """
        self._client = client
        self._base_url = base_url
    
    def list(self, category: Optional[str] = None) -> List[Tool]:
        """
        List available tools.
        
        Args:
            category: Filter by tool category
        
        Returns:
            List of Tool objects
        
        Raises:
            SunaError: If request fails
        """
        params = {}
        if category:
            params["category"] = category
        
        try:
            response = self._client.get(f"{self._base_url}/tools", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                tools_data = data
            elif isinstance(data, dict) and "tools" in data:
                tools_data = data["tools"]
            elif isinstance(data, dict) and "data" in data:
                tools_data = data["data"]
            else:
                tools_data = [data] if data else []
            
            return [Tool(**tool) for tool in tools_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list tools: {e.response.text}", status_code=e.response.status_code)
    
    def get(self, tool_name: str) -> Tool:
        """
        Get a tool by name.
        
        Args:
            tool_name: Tool name
        
        Returns:
            Tool object
        
        Raises:
            NotFoundError: If tool not found
            SunaError: If request fails
        """
        try:
            response = self._client.get(f"{self._base_url}/tools/{tool_name}")
            response.raise_for_status()
            return Tool(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Tool {tool_name} not found")
            raise SunaError(f"Failed to get tool: {e.response.text}", status_code=e.response.status_code)
    
    def execute(self, tool_name: str, **params: Any) -> ToolResult:
        """
        Execute a tool.
        
        Args:
            tool_name: Tool name
            **params: Tool parameters
        
        Returns:
            ToolResult object
        
        Raises:
            NotFoundError: If tool not found
            SunaError: If execution fails
        """
        payload = {
            "tool_name": tool_name,
            "parameters": params,
        }
        
        try:
            response = self._client.post(f"{self._base_url}/tools/execute", json=payload)
            response.raise_for_status()
            return ToolResult(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Tool {tool_name} not found")
            raise SunaError(f"Failed to execute tool: {e.response.text}", status_code=e.response.status_code)
