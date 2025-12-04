"""Web scraping tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class WebScraperTool(BaseTool):
    name = "web_scraper"
    description = "Scrape web pages and extract data"
    version = "1.0.0"
    category = ToolCategory.BROWSER.value
    
    def get_capabilities(self) -> List[str]:
        return ["fetch", "extract_text", "extract_links"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["fetch", "extract_text", "extract_links"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
