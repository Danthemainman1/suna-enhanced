"""PayPal payment processing."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class PayPalTool(BaseTool):
    name = "paypal"
    description = "Process payments with PayPal"
    version = "1.0.0"
    category = ToolCategory.FINANCE.value
    
    def get_capabilities(self) -> List[str]:
        return ["payment"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True, enum=["create_payment"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
