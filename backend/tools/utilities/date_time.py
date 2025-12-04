"""Date and time utilities."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class DateTimeTool(BaseTool):
    name = "date_time"
    description = "Date and time operations"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def get_capabilities(self) -> List[str]:
        return ["format", "parse", "calculate"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["format", "parse", "calculate"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
