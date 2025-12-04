"""Redis caching and pub/sub tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class RedisTool(BaseTool):
    name = "redis"
    description = "Redis caching and pub/sub operations"
    version = "1.0.0"
    category = ToolCategory.DATA.value
    
    def get_capabilities(self) -> List[str]:
        return ["cache", "pubsub"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True,
                             enum=["get", "set", "delete", "publish"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
