"""Stripe payment processing."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class StripeTool(BaseTool):
    name = "stripe"
    description = "Process payments with Stripe"
    version = "1.0.0"
    category = ToolCategory.FINANCE.value
    
    def get_capabilities(self) -> List[str]:
        return ["payment", "subscription", "customer"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["create_payment", "create_customer", "create_subscription"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
