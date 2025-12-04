"""Text processing utilities."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class TextProcessingTool(BaseTool):
    name = "text_processing"
    description = "Text manipulation and analysis"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def get_capabilities(self) -> List[str]:
        return ["tokenize", "sentiment", "summarize"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["tokenize", "sentiment", "summarize"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
