"""Local file storage tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class LocalStorageTool(BaseTool):
    name = "local_storage"
    description = "Local file system operations"
    version = "1.0.0"
    category = ToolCategory.STORAGE.value
    
    def get_capabilities(self) -> List[str]:
        return ["read", "write", "list", "delete"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True,
                             enum=["read", "write", "list", "delete"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
