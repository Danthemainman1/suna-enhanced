"""OpenAI API integration."""
from typing import List
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError

class OpenAITool(BaseTool):
    name = "openai"
    description = "OpenAI GPT models, DALL-E, Whisper"
    version = "1.0.0"
    category = ToolCategory.AI_ML.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ToolAuthenticationError("OpenAI API key required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["chat", "completion", "embedding", "image_generation", "transcription"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["chat", "complete", "embed", "image_generate", "transcribe"]),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(output={"action": kwargs.get("action")}, tool_name=self.name)
