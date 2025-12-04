"""Elasticsearch search and indexing tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class ElasticsearchTool(BaseTool):
    name = "elasticsearch"
    description = "Search and index documents in Elasticsearch"
    version = "1.0.0"
    category = ToolCategory.DATA.value
    
    def get_capabilities(self) -> List[str]:
        return ["search", "index", "bulk"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True,
                             enum=["search", "index", "delete"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
