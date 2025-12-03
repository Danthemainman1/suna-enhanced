"""
LLM provider module for Suna Ultra.

This module provides a unified interface for working with various LLM providers,
including local models (Ollama) and cloud providers (Anthropic, OpenAI).

Key Features:
- Local LLM support via Ollama for privacy and cost savings
- Cloud LLM support for high-quality results
- Hybrid routing for intelligent provider selection
- Unified API across all providers
- Async/await for all operations
"""

from .provider import LLMProvider, LLMResponse, ModelInfo
from .ollama import OllamaProvider
from .anthropic_provider import AnthropicProvider
from .openai_provider import OpenAIProvider
from .hybrid import HybridRouter, TaskComplexity
from .config import (
    LLMConfig,
    ProviderConfig,
    HybridConfig,
    get_config,
    set_config,
    reload_config
)


__all__ = [
    # Base classes
    "LLMProvider",
    "LLMResponse",
    "ModelInfo",
    
    # Providers
    "OllamaProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    
    # Hybrid routing
    "HybridRouter",
    "TaskComplexity",
    
    # Configuration
    "LLMConfig",
    "ProviderConfig",
    "HybridConfig",
    "get_config",
    "set_config",
    "reload_config",
]


__version__ = "1.0.0"
