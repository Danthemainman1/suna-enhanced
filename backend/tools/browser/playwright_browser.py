"""Playwright browser automation."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class PlaywrightBrowserTool(BaseTool):
    name = "playwright_browser"
    description = "Automate browser with Playwright"
    version = "1.0.0"
    category = ToolCategory.BROWSER.value
    
    def get_capabilities(self) -> List[str]:
        return ["navigate", "click", "type", "screenshot", "evaluate"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["navigate", "click", "screenshot"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
