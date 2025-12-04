"""Bing Search API tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class BingSearchTool(BaseTool):
    name = "bing_search"
    description = "Search the web with Bing"
    version = "1.0.0"
    category = ToolCategory.SEARCH.value
    
    def get_capabilities(self) -> List[str]:
        return ["web_search"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="query", type="string", description="Search query", required=True),
            ToolParameter(name="max_results", type="int", description="Max results", required=False),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"query": kwargs.get("query")}, tool_name=self.name)
