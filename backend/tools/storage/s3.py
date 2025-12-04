"""AWS S3 storage tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class S3Tool(BaseTool):
    name = "s3"
    description = "AWS S3 object storage operations"
    version = "1.0.0"
    category = ToolCategory.STORAGE.value
    
    def get_capabilities(self) -> List[str]:
        return ["upload", "download", "list", "delete"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["upload", "download", "list_objects", "delete"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
