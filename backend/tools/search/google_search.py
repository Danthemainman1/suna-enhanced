"""Google Search API tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class GoogleSearchTool(BaseTool):
    name = "google_search"
    description = "Search the web with Google"
    version = "1.0.0"
    category = ToolCategory.SEARCH.value
    
    def get_capabilities(self) -> List[str]:
        return ["web_search", "image_search", "news_search"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["search", "image_search", "news_search"]),
            ToolParameter(name="query", type="string", description="Search query", required=True),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(
            output={"query": kwargs.get("query"), "action": kwargs.get("action")},
            tool_name=self.name
        )
