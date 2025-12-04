"""HuggingFace Inference API tool."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class HuggingFaceTool(BaseTool):
    name = "huggingface"
    description = "Run inference on HuggingFace models"
    version = "1.0.0"
    category = ToolCategory.AI_ML.value
    
    def get_capabilities(self) -> List[str]:
        return ["inference", "text_generation", "image_classification"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["inference", "text_generation"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
