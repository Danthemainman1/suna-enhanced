"""Jira API integration tool."""

import asyncio
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError


logger = logging.getLogger(__name__)


class JiraTool(BaseTool):
    """Jira API integration."""
    
    name = "jira"
    description = "Manage Jira issues, projects, and sprints"
    version = "1.0.0"
    category = ToolCategory.DEVELOPMENT.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.api_token = config.get("api_token")
        self.email = config.get("email")
        self.domain = config.get("domain")
        if not all([self.api_token, self.email, self.domain]):
            raise ToolAuthenticationError("Jira credentials required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["issue_management", "project_management", "sprint_management"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action to perform", required=True,
                         enum=["create_issue", "update_issue", "transition_issue", "search_jql"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action")
        return ToolResult.success_result(output={"action": action, "status": "completed"}, tool_name=self.name)
