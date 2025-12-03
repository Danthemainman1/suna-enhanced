"""
Anthropic Claude provider for cloud LLM support.

This module provides integration with Anthropic's Claude models,
including Claude Opus 4.5 and other versions.
"""

import os
from typing import AsyncGenerator, Optional
import logging

from anthropic import AsyncAnthropic
from anthropic.types import Message

from .provider import LLMProvider, LLMResponse, ModelInfo


logger = logging.getLogger(__name__)


# Claude model metadata
CLAUDE_MODELS = {
    "claude-opus-4-20250514": {
        "context_window": 200000,
        "max_output_tokens": 16000,
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
    },
    "claude-3-5-sonnet-20241022": {
        "context_window": 200000,
        "max_output_tokens": 8192,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
    "claude-3-opus-20240229": {
        "context_window": 200000,
        "max_output_tokens": 4096,
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
    },
    "claude-3-sonnet-20240229": {
        "context_window": 200000,
        "max_output_tokens": 4096,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
    "claude-3-haiku-20240307": {
        "context_window": 200000,
        "max_output_tokens": 4096,
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.00125,
    },
}


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude integration for high-quality cloud LLM.
    
    Supports all Claude models including the latest Claude Opus 4.5,
    with streaming responses and advanced features.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "claude-3-5-sonnet-20241022",
        max_retries: int = 3,
        timeout: int = 600,
        **config
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            default_model: Default model to use
            max_retries: Number of retries on failure
            timeout: Request timeout in seconds
            **config: Additional configuration options
        """
        super().__init__(**config)
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.default_model = default_model
        self.client = AsyncAnthropic(
            api_key=self.api_key,
            max_retries=max_retries,
            timeout=timeout
        )
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion using Claude.
        
        Args:
            prompt: The input prompt text
            model: Model name (e.g., 'claude-opus-4-20250514')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: Optional system prompt
            **kwargs: Additional Anthropic-specific parameters
            
        Returns:
            LLMResponse with generated content
        """
        model_name = model or self.default_model
        max_tokens = max_tokens or 4096
        
        try:
            message_params = {
                "model": model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            }
            
            if system:
                message_params["system"] = system
            
            # Add any additional parameters
            message_params.update(kwargs)
            
            message: Message = await self.client.messages.create(**message_params)
            
            # Extract text content
            content = ""
            for block in message.content:
                if hasattr(block, "text"):
                    content += block.text
            
            return LLMResponse(
                content=content,
                model=model_name,
                provider="anthropic",
                usage={
                    "prompt_tokens": message.usage.input_tokens,
                    "completion_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens
                },
                finish_reason=message.stop_reason,
                metadata={
                    "message_id": message.id,
                    "stop_sequence": message.stop_sequence
                }
            )
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise Exception(f"Failed to generate completion: {e}")
    
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion using Claude.
        
        Args:
            prompt: The input prompt text
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: Optional system prompt
            **kwargs: Additional parameters
            
        Yields:
            Generated text chunks
        """
        model_name = model or self.default_model
        max_tokens = max_tokens or 4096
        
        try:
            message_params = {
                "model": model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            }
            
            if system:
                message_params["system"] = system
            
            message_params.update(kwargs)
            
            async with self.client.messages.stream(**message_params) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            raise Exception(f"Failed to stream completion: {e}")
    
    async def get_model_info(self, model: Optional[str] = None) -> ModelInfo:
        """
        Get information about a Claude model.
        
        Args:
            model: Model name
            
        Returns:
            ModelInfo with model metadata
        """
        model_name = model or self.default_model
        
        if model_name not in CLAUDE_MODELS:
            # Return default info for unknown models
            return ModelInfo(
                name=model_name,
                provider="anthropic",
                context_window=200000,
                max_output_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                metadata={"family": "claude"}
            )
        
        info = CLAUDE_MODELS[model_name]
        return ModelInfo(
            name=model_name,
            provider="anthropic",
            context_window=info["context_window"],
            max_output_tokens=info["max_output_tokens"],
            supports_streaming=True,
            supports_function_calling=True,
            cost_per_1k_input_tokens=info["cost_per_1k_input"],
            cost_per_1k_output_tokens=info["cost_per_1k_output"],
            metadata={"family": "claude"}
        )
    
    async def health_check(self) -> bool:
        """
        Check if Anthropic API is accessible.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Try a minimal API call to verify connectivity
            await self.client.messages.create(
                model=self.default_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.warning(f"Anthropic health check failed: {e}")
            return False
    
    async def list_models(self) -> list[str]:
        """
        List available Claude models.
        
        Returns:
            List of model names
        """
        return list(CLAUDE_MODELS.keys())
    
    async def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens in text using Anthropic's tokenizer.
        
        Args:
            text: Text to count tokens for
            model: Model name (for model-specific tokenization)
            
        Returns:
            Token count
        """
        model_name = model or self.default_model
        
        try:
            # Anthropic provides a count_tokens method
            result = await self.client.messages.count_tokens(
                model=model_name,
                messages=[{"role": "user", "content": text}]
            )
            return result.input_tokens
        except Exception as e:
            logger.warning(f"Token counting failed, using estimate: {e}")
            # Fallback to rough estimate (4 chars per token)
            return len(text) // 4
