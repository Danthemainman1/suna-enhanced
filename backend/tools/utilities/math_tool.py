"""Mathematical operations."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class MathTool(BaseTool):
    name = "math"
    description = "Perform mathematical calculations"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def get_capabilities(self) -> List[str]:
        return ["calculate", "evaluate"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="expression", type="string", description="Math expression", required=True),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"expression": kwargs.get("expression")}, tool_name=self.name)
