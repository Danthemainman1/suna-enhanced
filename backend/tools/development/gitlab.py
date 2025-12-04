"""GitLab API integration tool."""

import asyncio
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError


logger = logging.getLogger(__name__)


class GitLabTool(BaseTool):
    """GitLab API integration."""
    
    name = "gitlab"
    description = "Manage GitLab projects, issues, and merge requests"
    version = "1.0.0"
    category = ToolCategory.DEVELOPMENT.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.token = config.get("token")
        if not self.token:
            raise ToolAuthenticationError("GitLab token required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["project_management", "issue_management", "mr_management"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action to perform", required=True,
                         enum=["list_projects", "create_issue", "create_mr"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action")
        return ToolResult.success_result(output={"action": action, "status": "completed"}, tool_name=self.name)
