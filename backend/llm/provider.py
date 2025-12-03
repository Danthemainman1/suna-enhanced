"""
Base abstract class for LLM providers.

This module defines the interface that all LLM providers must implement,
ensuring consistent behavior across different LLM backends (local, cloud, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Model metadata information."""
    
    name: str = Field(..., description="Model name/identifier")
    provider: str = Field(..., description="Provider name (e.g., 'ollama', 'anthropic')")
    context_window: int = Field(..., description="Maximum context window size in tokens")
    max_output_tokens: Optional[int] = Field(None, description="Maximum output tokens")
    supports_streaming: bool = Field(True, description="Whether the model supports streaming")
    supports_function_calling: bool = Field(False, description="Whether the model supports function calling")
    cost_per_1k_input_tokens: Optional[float] = Field(None, description="Cost per 1K input tokens (USD)")
    cost_per_1k_output_tokens: Optional[float] = Field(None, description="Cost per 1K output tokens (USD)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific metadata")


class LLMResponse(BaseModel):
    """Standardized LLM response."""
    
    content: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Model used for generation")
    provider: str = Field(..., description="Provider name")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    All LLM integrations must inherit from this class and implement
    the required abstract methods to ensure consistent behavior.
    """
    
    def __init__(self, **config):
        """
        Initialize the provider with configuration.
        
        Args:
            **config: Provider-specific configuration options
        """
        self.config = config
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The input prompt text
            model: Optional model name (uses default if not specified)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse with the generated content
            
        Raises:
            Exception: If generation fails
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion for the given prompt.
        
        Args:
            prompt: The input prompt text
            model: Optional model name (uses default if not specified)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Generated text chunks as they become available
            
        Raises:
            Exception: If streaming fails
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model: Optional[str] = None) -> ModelInfo:
        """
        Get metadata information about a model.
        
        Args:
            model: Optional model name (uses default if not specified)
            
        Returns:
            ModelInfo with model metadata
            
        Raises:
            Exception: If model info cannot be retrieved
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify that the provider is available and operational.
        
        Returns:
            True if the provider is healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> list[str]:
        """
        List all available models for this provider.
        
        Returns:
            List of model names/identifiers
            
        Raises:
            Exception: If models cannot be listed
        """
        pass
