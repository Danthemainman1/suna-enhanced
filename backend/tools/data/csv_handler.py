"""CSV file handling tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class CSVHandlerTool(BaseTool):
    name = "csv_handler"
    description = "Read and write CSV files"
    version = "1.0.0"
    category = ToolCategory.DATA.value
    
    def get_capabilities(self) -> List[str]:
        return ["read", "write", "parse"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True,
                             enum=["read", "write", "parse"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
