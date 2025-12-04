"""Stability AI image generation."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult

class StabilityAITool(BaseTool):
    name = "stability_ai"
    description = "Generate images with Stable Diffusion"
    version = "1.0.0"
    category = ToolCategory.AI_ML.value
    
    def get_capabilities(self) -> List[str]:
        return ["image_generation"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [ToolParameter(name="action", type="string", description="Action", required=True, enum=["generate"])]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
