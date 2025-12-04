"""
OpenAI provider for cloud LLM support.

This module provides integration with OpenAI's GPT models,
including GPT-4 and GPT-3.5 with function calling support.
"""

import os
from typing import AsyncGenerator, Optional, Dict, Any
import logging

from openai import AsyncOpenAI

from .provider import LLMProvider, LLMResponse, ModelInfo


logger = logging.getLogger(__name__)


# OpenAI model metadata
OPENAI_MODELS = {
    "gpt-4o": {
        "context_window": 128000,
        "max_output_tokens": 16384,
        "cost_per_1k_input": 0.005,
        "cost_per_1k_output": 0.015,
    },
    "gpt-4o-mini": {
        "context_window": 128000,
        "max_output_tokens": 16384,
        "cost_per_1k_input": 0.00015,
        "cost_per_1k_output": 0.0006,
    },
    "gpt-4-turbo": {
        "context_window": 128000,
        "max_output_tokens": 4096,
        "cost_per_1k_input": 0.01,
        "cost_per_1k_output": 0.03,
    },
    "gpt-4": {
        "context_window": 8192,
        "max_output_tokens": 8192,
        "cost_per_1k_input": 0.03,
        "cost_per_1k_output": 0.06,
    },
    "gpt-3.5-turbo": {
        "context_window": 16385,
        "max_output_tokens": 4096,
        "cost_per_1k_input": 0.0005,
        "cost_per_1k_output": 0.0015,
    },
}


class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT integration for cloud LLM.
    
    Supports GPT-4, GPT-3.5, and other OpenAI models with
    streaming responses and function calling capabilities.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gpt-4o",
        organization: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 600,
        **config
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            default_model: Default model to use
            organization: Optional organization ID
            max_retries: Number of retries on failure
            timeout: Request timeout in seconds
            **config: Additional configuration options
        """
        super().__init__(**config)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.default_model = default_model
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            organization=organization,
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
        functions: Optional[list[Dict[str, Any]]] = None,
        function_call: Optional[str | Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion using OpenAI.
        
        Args:
            prompt: The input prompt text
            model: Model name (e.g., 'gpt-4o', 'gpt-3.5-turbo')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system: Optional system prompt
            functions: Optional function definitions for function calling
            function_call: Optional function call control
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            LLMResponse with generated content
        """
        model_name = model or self.default_model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                completion_params["max_tokens"] = max_tokens
            
            if functions:
                completion_params["functions"] = functions
            
            if function_call:
                completion_params["function_call"] = function_call
            
            # Add any additional parameters
            completion_params.update(kwargs)
            
            response = await self.client.chat.completions.create(**completion_params)
            
            choice = response.choices[0]
            message = choice.message
            
            # Handle function call response
            content = message.content or ""
            metadata = {}
            
            if hasattr(message, "function_call") and message.function_call:
                metadata["function_call"] = {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            
            return LLMResponse(
                content=content,
                model=model_name,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                finish_reason=choice.finish_reason,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
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
        Stream a completion using OpenAI.
        
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
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            
            if max_tokens:
                completion_params["max_tokens"] = max_tokens
            
            completion_params.update(kwargs)
            
            stream = await self.client.chat.completions.create(**completion_params)
            
            async for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise Exception(f"Failed to stream completion: {e}")
    
    async def get_model_info(self, model: Optional[str] = None) -> ModelInfo:
        """
        Get information about an OpenAI model.
        
        Args:
            model: Model name
            
        Returns:
            ModelInfo with model metadata
        """
        model_name = model or self.default_model
        
        if model_name not in OPENAI_MODELS:
            # Return default info for unknown models
            return ModelInfo(
                name=model_name,
                provider="openai",
                context_window=8192,
                max_output_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                metadata={"family": "gpt"}
            )
        
        info = OPENAI_MODELS[model_name]
        return ModelInfo(
            name=model_name,
            provider="openai",
            context_window=info["context_window"],
            max_output_tokens=info["max_output_tokens"],
            supports_streaming=True,
            supports_function_calling=True,
            cost_per_1k_input_tokens=info["cost_per_1k_input"],
            cost_per_1k_output_tokens=info["cost_per_1k_output"],
            metadata={"family": "gpt"}
        )
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Try listing models to verify API connectivity
            await self.client.models.list()
            return True
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
    
    async def list_models(self) -> list[str]:
        """
        List available OpenAI models.
        
        Returns:
            List of model names
        """
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.warning(f"Failed to list OpenAI models: {e}")
            # Return known models as fallback
            return list(OPENAI_MODELS.keys())
