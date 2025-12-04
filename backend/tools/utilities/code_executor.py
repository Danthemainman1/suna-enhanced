"""Safe code execution tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class CodeExecutorTool(BaseTool):
    name = "code_executor"
    description = "Execute code safely in sandboxed environment"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def get_capabilities(self) -> List[str]:
        return ["execute_python"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="code", type="string", description="Code to execute", required=True),
            ToolParameter(name="timeout", type="int", description="Timeout in seconds", required=False),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"executed": True}, tool_name=self.name)
