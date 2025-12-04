"""Wikipedia search and retrieval."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class WikipediaTool(BaseTool):
    name = "wikipedia"
    description = "Search and retrieve Wikipedia articles"
    version = "1.0.0"
    category = ToolCategory.SEARCH.value
    
    def get_capabilities(self) -> List[str]:
        return ["search", "get_page", "get_summary"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["search", "get_page", "get_summary"]),
            ToolParameter(name="query", type="string", description="Search query or page title", required=True),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(
            output={"query": kwargs.get("query"), "action": kwargs.get("action")},
            tool_name=self.name
        )
