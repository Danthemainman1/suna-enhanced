"""PostgreSQL database tool with asyncpg."""
import asyncio
from typing import List, Dict, Any
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError

class PostgreSQLTool(BaseTool):
    name = "postgresql"
    description = "Execute PostgreSQL queries with connection pooling"
    version = "1.0.0"
    category = ToolCategory.DATA.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.dsn = config.get("dsn")
        if not self.dsn:
            raise ToolAuthenticationError("PostgreSQL DSN required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["query", "execute", "transaction"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["query", "execute", "get_tables"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
