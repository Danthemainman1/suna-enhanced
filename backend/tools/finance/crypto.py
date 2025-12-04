"""Cryptocurrency tools."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class CryptoTool(BaseTool):
    name = "crypto"
    description = "Cryptocurrency operations and price tracking"
    version = "1.0.0"
    category = ToolCategory.FINANCE.value
    
    def get_capabilities(self) -> List[str]:
        return ["price_check", "transaction"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True, enum=["get_price"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
