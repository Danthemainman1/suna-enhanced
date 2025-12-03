"""
Ollama provider for local LLM support.

This module provides integration with Ollama for running local models
like Llama, Mistral, and others on your own infrastructure.
"""

import aiohttp
from typing import AsyncGenerator, Optional, Any, Dict
import logging

from .provider import LLMProvider, LLMResponse, ModelInfo


logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """
    Ollama integration for local LLM models.
    
    Supports running models like Llama 3.1, Mistral, and other open models
    locally for privacy, cost savings, and complete control.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.1",
        timeout: int = 300,
        **config
    ):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            default_model: Default model to use (default: llama3.1)
            timeout: Request timeout in seconds (default: 300)
            **config: Additional configuration options
        """
        super().__init__(**config)
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion using Ollama.
        
        Args:
            prompt: The input prompt text
            model: Model name (e.g., 'llama3.1', 'mistral')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Ollama-specific parameters
            
        Returns:
            LLMResponse with generated content
        """
        model_name = model or self.default_model
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        # Add any additional options
        if kwargs:
            payload["options"].update(kwargs)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    return LLMResponse(
                        content=result.get("response", ""),
                        model=model_name,
                        provider="ollama",
                        usage={
                            "prompt_tokens": result.get("prompt_eval_count", 0),
                            "completion_tokens": result.get("eval_count", 0),
                            "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                        },
                        finish_reason=result.get("done_reason"),
                        metadata={
                            "eval_duration": result.get("eval_duration"),
                            "load_duration": result.get("load_duration"),
                            "total_duration": result.get("total_duration")
                        }
                    )
        except aiohttp.ClientError as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"Failed to generate completion: {e}")
    
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion using Ollama.
        
        Args:
            prompt: The input prompt text
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Generated text chunks
        """
        model_name = model or self.default_model
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        if kwargs:
            payload["options"].update(kwargs)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.content:
                        if line:
                            import json
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
        except aiohttp.ClientError as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise Exception(f"Failed to stream completion: {e}")
    
    async def get_model_info(self, model: Optional[str] = None) -> ModelInfo:
        """
        Get information about a specific model.
        
        Args:
            model: Model name
            
        Returns:
            ModelInfo with model metadata
        """
        model_name = model or self.default_model
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/show",
                    json={"name": model_name},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    # Parse model info from Ollama response
                    modelfile = result.get("modelfile", "")
                    parameters = result.get("parameters", "")
                    
                    # Try to extract context window from parameters
                    context_window = 4096  # Default
                    if "num_ctx" in parameters:
                        try:
                            import re
                            match = re.search(r"num_ctx\s+(\d+)", parameters)
                            if match:
                                context_window = int(match.group(1))
                        except Exception:
                            pass
                    
                    return ModelInfo(
                        name=model_name,
                        provider="ollama",
                        context_window=context_window,
                        max_output_tokens=None,
                        supports_streaming=True,
                        supports_function_calling=False,
                        cost_per_1k_input_tokens=0.0,  # Local models are free
                        cost_per_1k_output_tokens=0.0,
                        metadata={
                            "size": result.get("size"),
                            "format": result.get("format"),
                            "family": result.get("details", {}).get("family"),
                            "parameter_size": result.get("details", {}).get("parameter_size")
                        }
                    )
        except aiohttp.ClientError as e:
            logger.error(f"Failed to get Ollama model info: {e}")
            raise Exception(f"Failed to get model info: {e}")
    
    async def health_check(self) -> bool:
        """
        Check if Ollama is running and accessible.
        
        Returns:
            True if Ollama is healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
    
    async def list_models(self) -> list[str]:
        """
        List all locally available models.
        
        Returns:
            List of model names
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    models = result.get("models", [])
                    return [m["name"] for m in models]
        except aiohttp.ClientError as e:
            logger.error(f"Failed to list Ollama models: {e}")
            raise Exception(f"Failed to list models: {e}")
    
    async def pull_model(self, model: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Pull a model from Ollama library.
        
        Args:
            model: Model name to pull (e.g., 'llama3.1', 'mistral')
            
        Yields:
            Progress updates during model download
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model, "stream": True},
                    timeout=aiohttp.ClientTimeout(total=3600)  # 1 hour for large models
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.content:
                        if line:
                            import json
                            try:
                                progress = json.loads(line)
                                yield progress
                            except json.JSONDecodeError:
                                continue
        except aiohttp.ClientError as e:
            logger.error(f"Failed to pull Ollama model: {e}")
            raise Exception(f"Failed to pull model: {e}")
