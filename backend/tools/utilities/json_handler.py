"""JSON parsing and manipulation."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class JSONHandlerTool(BaseTool):
    name = "json_handler"
    description = "Parse, validate, and manipulate JSON"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def get_capabilities(self) -> List[str]:
        return ["parse", "validate", "transform"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["parse", "validate", "transform"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
