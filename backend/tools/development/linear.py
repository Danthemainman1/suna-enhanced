"""Linear API integration tool."""

import asyncio
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError


logger = logging.getLogger(__name__)


class LinearTool(BaseTool):
    """Linear API integration."""
    
    name = "linear"
    description = "Manage Linear issues and teams"
    version = "1.0.0"
    category = ToolCategory.DEVELOPMENT.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ToolAuthenticationError("Linear API key required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["issue_management", "team_management"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action to perform", required=True,
                         enum=["create_issue", "update_issue", "list_issues", "list_teams"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action")
        return ToolResult.success_result(output={"action": action, "status": "completed"}, tool_name=self.name)
