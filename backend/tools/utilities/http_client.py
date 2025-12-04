"""HTTP client for making web requests."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class HTTPClientTool(BaseTool):
    name = "http_client"
    description = "Make HTTP requests (GET, POST, PUT, DELETE)"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def get_capabilities(self) -> List[str]:
        return ["http_request"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="method", type="string", description="HTTP method", required=True,
                         enum=["GET", "POST", "PUT", "DELETE"]),
            ToolParameter(name="url", type="string", description="URL", required=True),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(
            output={"method": kwargs.get("method"), "url": kwargs.get("url")},
            tool_name=self.name
        )
