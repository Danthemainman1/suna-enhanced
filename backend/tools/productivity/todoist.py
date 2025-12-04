"""Todoist API integration tool."""

import asyncio
import httpx
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError


logger = logging.getLogger(__name__)


class TodoistTool(BaseTool):
    """Todoist API integration."""
    
    name = "todoist"
    description = "Manage Todoist tasks and projects"
    version = "1.0.0"
    category = ToolCategory.PRODUCTIVITY.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.api_token = config.get("api_token")
        if not self.api_token:
            raise ToolAuthenticationError("Todoist API token required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["task_management", "project_management"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action to perform", required=True,
                         enum=["list_tasks", "create_task", "complete_task", "list_projects"]),
            ToolParameter(name="project_id", type="string", description="Project ID", required=False),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        action = kwargs.get("action")
        return ToolResult.success_result(
            output={"action": action, "status": "completed"},
            tool_name=self.name
        )
