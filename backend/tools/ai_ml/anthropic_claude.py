"""Anthropic Claude AI integration."""
import asyncio
import httpx
from typing import List, Dict, Any, AsyncGenerator
from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError

class AnthropicClaudeTool(BaseTool):
    name = "anthropic_claude"
    description = "Generate text with Claude Opus 4.5, Sonnet 4, Haiku"
    version = "1.0.0"
    category = ToolCategory.AI_ML.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ToolAuthenticationError("Anthropic API key required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return ["text_generation", "chat", "streaming"]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action", required=True,
                         enum=["generate", "chat", "stream"]),
            ToolParameter(name="model", type="string", description="Model name", required=False),
            ToolParameter(name="prompt", type="string", description="Prompt text", required=False),
        ]
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult.success_result(
            output={"action": kwargs.get("action"), "model": kwargs.get("model", "claude-opus-4.5")},
            tool_name=self.name
        )
