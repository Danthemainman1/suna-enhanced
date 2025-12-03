"""
Configuration management for LLM providers.

This module handles configuration for all LLM providers,
including API keys, model preferences, and routing settings.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging


logger = logging.getLogger(__name__)


class ProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""
    
    enabled: bool = Field(True, description="Whether this provider is enabled")
    api_key: Optional[str] = Field(None, description="API key (if required)")
    default_model: Optional[str] = Field(None, description="Default model to use")
    base_url: Optional[str] = Field(None, description="Base URL (for local providers)")
    timeout: int = Field(600, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retries")
    extra_config: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific config")


class HybridConfig(BaseModel):
    """Configuration for hybrid routing."""
    
    enabled: bool = Field(False, description="Whether hybrid routing is enabled")
    prefer_local: bool = Field(True, description="Prefer local over cloud when possible")
    max_local_tokens: int = Field(8000, description="Max tokens for local provider")
    complexity_threshold: str = Field("medium", description="Complexity threshold for cloud routing")
    enable_fallback: bool = Field(True, description="Enable fallback on provider failure")


class LLMConfig(BaseModel):
    """
    Main LLM configuration.
    
    This class manages all LLM provider configurations and provides
    helper methods for common configuration tasks.
    """
    
    default_provider: str = Field("anthropic", description="Default provider to use")
    
    # Provider configurations
    ollama: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(
            enabled=True,
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            default_model=os.environ.get("OLLAMA_MODEL", "llama3.1")
        ),
        description="Ollama configuration"
    )
    
    anthropic: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(
            enabled=bool(os.environ.get("ANTHROPIC_API_KEY")),
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            default_model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        ),
        description="Anthropic configuration"
    )
    
    openai: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(
            enabled=bool(os.environ.get("OPENAI_API_KEY")),
            api_key=os.environ.get("OPENAI_API_KEY"),
            default_model=os.environ.get("OPENAI_MODEL", "gpt-4o")
        ),
        description="OpenAI configuration"
    )
    
    # Hybrid routing configuration
    hybrid: HybridConfig = Field(
        default_factory=lambda: HybridConfig(
            enabled=os.environ.get("HYBRID_ROUTING_ENABLED", "false").lower() == "true",
            prefer_local=os.environ.get("PREFER_LOCAL", "true").lower() == "true",
            max_local_tokens=int(os.environ.get("MAX_LOCAL_TOKENS", "8000")),
            complexity_threshold=os.environ.get("COMPLEXITY_THRESHOLD", "medium"),
            enable_fallback=os.environ.get("ENABLE_FALLBACK", "true").lower() == "true"
        ),
        description="Hybrid routing configuration"
    )
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Create configuration from environment variables.
        
        Environment variables:
        - DEFAULT_LLM_PROVIDER: Default provider (ollama, anthropic, openai)
        - OLLAMA_BASE_URL: Ollama base URL
        - OLLAMA_MODEL: Ollama default model
        - ANTHROPIC_API_KEY: Anthropic API key
        - ANTHROPIC_MODEL: Anthropic default model
        - OPENAI_API_KEY: OpenAI API key
        - OPENAI_MODEL: OpenAI default model
        - HYBRID_ROUTING_ENABLED: Enable hybrid routing (true/false)
        - PREFER_LOCAL: Prefer local models (true/false)
        - MAX_LOCAL_TOKENS: Max tokens for local provider
        - COMPLEXITY_THRESHOLD: Complexity threshold (simple/medium/complex/very_complex)
        - ENABLE_FALLBACK: Enable fallback (true/false)
        
        Returns:
            LLMConfig instance
        """
        default_provider = os.environ.get("DEFAULT_LLM_PROVIDER", "anthropic")
        
        return cls(default_provider=default_provider)
    
    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name (ollama, anthropic, openai)
            
        Returns:
            ProviderConfig if found, None otherwise
        """
        if provider == "ollama":
            return self.ollama
        elif provider == "anthropic":
            return self.anthropic
        elif provider == "openai":
            return self.openai
        else:
            logger.warning(f"Unknown provider: {provider}")
            return None
    
    def is_provider_enabled(self, provider: str) -> bool:
        """
        Check if a provider is enabled.
        
        Args:
            provider: Provider name
            
        Returns:
            True if enabled, False otherwise
        """
        config = self.get_provider_config(provider)
        return config.enabled if config else False
    
    def get_available_providers(self) -> list[str]:
        """
        Get list of available (enabled) providers.
        
        Returns:
            List of provider names
        """
        providers = []
        
        if self.ollama.enabled:
            providers.append("ollama")
        
        if self.anthropic.enabled and self.anthropic.api_key:
            providers.append("anthropic")
        
        if self.openai.enabled and self.openai.api_key:
            providers.append("openai")
        
        return providers
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check if at least one provider is enabled
        available = self.get_available_providers()
        if not available:
            errors.append("No LLM providers are available. Configure at least one provider.")
        
        # Check if default provider is available
        if self.default_provider not in available:
            errors.append(
                f"Default provider '{self.default_provider}' is not available. "
                f"Available providers: {', '.join(available)}"
            )
        
        # Check hybrid routing requirements
        if self.hybrid.enabled:
            if len(available) < 2:
                errors.append("Hybrid routing requires at least 2 providers to be available")
            
            # Check if Ollama is available for local routing
            if self.hybrid.prefer_local and "ollama" not in available:
                errors.append("Hybrid routing with prefer_local=True requires Ollama to be available")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation (with API keys masked)
        """
        config_dict = self.model_dump()
        
        # Mask API keys
        if config_dict.get("anthropic", {}).get("api_key"):
            config_dict["anthropic"]["api_key"] = "***MASKED***"
        
        if config_dict.get("openai", {}).get("api_key"):
            config_dict["openai"]["api_key"] = "***MASKED***"
        
        return config_dict


# Global configuration instance
_config: Optional[LLMConfig] = None


def get_config() -> LLMConfig:
    """
    Get global LLM configuration instance.
    
    Returns:
        LLMConfig instance
    """
    global _config
    if _config is None:
        _config = LLMConfig.from_env()
    return _config


def set_config(config: LLMConfig) -> None:
    """
    Set global LLM configuration instance.
    
    Args:
        config: LLMConfig instance
    """
    global _config
    _config = config


def reload_config() -> LLMConfig:
    """
    Reload configuration from environment.
    
    Returns:
        New LLMConfig instance
    """
    global _config
    _config = LLMConfig.from_env()
    return _config
