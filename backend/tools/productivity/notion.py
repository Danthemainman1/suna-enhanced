"""
Notion API integration tool.

Provides comprehensive Notion workspace management.
"""

import asyncio
import httpx
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError, ToolRateLimitError


logger = logging.getLogger(__name__)


class NotionTool(BaseTool):
    """
    Notion API integration.
    
    Supports:
    - Page creation and updates
    - Database queries
    - Block appending
    - Search functionality
    """
    
    name = "notion"
    description = "Manage Notion pages, databases, and content"
    version = "1.0.0"
    category = ToolCategory.PRODUCTIVITY.value
    
    def __init__(self, **config):
        """
        Initialize Notion tool.
        
        Args:
            token: Notion integration token (required)
            version: Notion API version (default: 2022-06-28)
        """
        super().__init__(**config)
        self.token = config.get("token")
        self.base_url = "https://api.notion.com/v1"
        self.version = config.get("version", "2022-06-28")
        
        if not self.token:
            raise ToolAuthenticationError(
                "Notion integration token required",
                tool_name=self.name
            )
    
    def get_capabilities(self) -> List[str]:
        """Get Notion tool capabilities."""
        return [
            "page_management",
            "database_management",
            "content_editing",
            "search",
        ]
    
    def get_parameters(self) -> List[ToolParameter]:
        """Get Notion tool parameters."""
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=[
                    "create_page",
                    "get_page",
                    "update_page",
                    "query_database",
                    "create_database",
                    "search",
                    "append_blocks",
                ]
            ),
            ToolParameter(
                name="parent_id",
                type="string",
                description="Parent page or database ID",
                required=False
            ),
            ToolParameter(
                name="title",
                type="string",
                description="Page or database title",
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
        """Make authenticated request to Notion API with retries."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.version,
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
                        retry_after = int(response.headers.get("Retry-After", 60))
                        if attempt < retries - 1:
                            logger.warning(f"Rate limited, retrying after {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        raise ToolRateLimitError(
                            f"Rate limited by Notion API",
                            tool_name=self.name,
                            retry_after=retry_after
                        )
                    
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
    
    async def create_page(
        self,
        parent_id: str,
        title: str,
        content: Optional[List[Dict]] = None
    ) -> ToolResult:
        """Create a new Notion page."""
        data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }
        
        if content:
            data["children"] = content
        
        result = await self._make_request("POST", "pages", data)
        
        return ToolResult.success_result(
            output={"page_id": result.get("id"), "url": result.get("url")},
            tool_name=self.name,
            metadata={"action": "create_page"}
        )
    
    async def get_page(self, page_id: str) -> ToolResult:
        """Get a Notion page."""
        result = await self._make_request("GET", f"pages/{page_id}")
        
        return ToolResult.success_result(
            output=result,
            tool_name=self.name,
            metadata={"action": "get_page"}
        )
    
    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any]
    ) -> ToolResult:
        """Update a Notion page."""
        data = {"properties": properties}
        
        result = await self._make_request("PATCH", f"pages/{page_id}", data)
        
        return ToolResult.success_result(
            output={"page_id": result.get("id")},
            tool_name=self.name,
            metadata={"action": "update_page"}
        )
    
    async def query_database(
        self,
        database_id: str,
        filter_obj: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> ToolResult:
        """Query a Notion database."""
        data = {}
        
        if filter_obj:
            data["filter"] = filter_obj
        if sorts:
            data["sorts"] = sorts
        
        result = await self._make_request(
            "POST",
            f"databases/{database_id}/query",
            data
        )
        
        return ToolResult.success_result(
            output=result.get("results", []),
            tool_name=self.name,
            metadata={"action": "query_database", "count": len(result.get("results", []))}
        )
    
    async def search(self, query: str) -> ToolResult:
        """Search Notion workspace."""
        data = {"query": query}
        
        result = await self._make_request("POST", "search", data)
        
        return ToolResult.success_result(
            output=result.get("results", []),
            tool_name=self.name,
            metadata={"action": "search", "count": len(result.get("results", []))}
        )
    
    async def append_blocks(
        self,
        page_id: str,
        blocks: List[Dict[str, Any]]
    ) -> ToolResult:
        """Append blocks to a page."""
        data = {"children": blocks}
        
        result = await self._make_request(
            "PATCH",
            f"blocks/{page_id}/children",
            data
        )
        
        return ToolResult.success_result(
            output={"success": True, "blocks_added": len(blocks)},
            tool_name=self.name,
            metadata={"action": "append_blocks"}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute Notion action."""
        action = kwargs.get("action")
        
        if action == "create_page":
            return await self.create_page(
                parent_id=kwargs.get("parent_id"),
                title=kwargs.get("title"),
                content=kwargs.get("content")
            )
        elif action == "get_page":
            return await self.get_page(page_id=kwargs.get("page_id"))
        elif action == "update_page":
            return await self.update_page(
                page_id=kwargs.get("page_id"),
                properties=kwargs.get("properties")
            )
        elif action == "query_database":
            return await self.query_database(
                database_id=kwargs.get("database_id"),
                filter_obj=kwargs.get("filter"),
                sorts=kwargs.get("sorts")
            )
        elif action == "search":
            return await self.search(query=kwargs.get("query"))
        elif action == "append_blocks":
            return await self.append_blocks(
                page_id=kwargs.get("page_id"),
                blocks=kwargs.get("blocks")
            )
        else:
            return ToolResult.error_result(
                error=f"Unknown action: {action}",
                tool_name=self.name
            )
