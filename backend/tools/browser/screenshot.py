"""Screenshot capture tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class ScreenshotTool(BaseTool):
    name = "screenshot"
    description = "Capture screenshots of web pages"
    version = "1.0.0"
    category = ToolCategory.BROWSER.value
    
    def get_capabilities(self) -> List[str]:
        return ["capture"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="url", type="string", description="URL to capture", required=True)]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"url": kwargs.get("url")}, tool_name=self.name)
