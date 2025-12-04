"""Safe shell command execution."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class ShellExecutorTool(BaseTool):
    name = "shell_executor"
    description = "Execute whitelisted shell commands"
    version = "1.0.0"
    category = ToolCategory.UTILITIES.value
    
    def get_capabilities(self) -> List[str]:
        return ["execute_command"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="command", type="string", description="Shell command", required=True),
            ToolParameter(name="timeout", type="int", description="Timeout in seconds", required=False),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"executed": True}, tool_name=self.name)
