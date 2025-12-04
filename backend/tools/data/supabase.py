"""Supabase database and auth tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class SupabaseTool(BaseTool):
    name = "supabase"
    description = "Interact with Supabase database and services"
    version = "1.0.0"
    category = ToolCategory.DATA.value
    
    def get_capabilities(self) -> List[str]:
        return ["query", "insert", "update", "delete", "rpc"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True,
                             enum=["query", "insert", "update", "delete"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
