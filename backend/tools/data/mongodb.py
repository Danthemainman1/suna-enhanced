"""MongoDB tool with motor async driver."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError

class MongoDBTool(BaseTool):
    name = "mongodb"
    description = "Interact with MongoDB databases"
    version = "1.0.0"
    category = ToolCategory.DATA.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.connection_string = config.get("connection_string")
        if not self.connection_string:
            raise ToolAuthenticationError("MongoDB connection string required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["find", "insert", "update", "delete", "aggregate"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True,
                             enum=["find", "insert_one", "update_one", "delete_one"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
