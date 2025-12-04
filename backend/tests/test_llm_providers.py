"""
Tests for LLM providers.

This module tests all LLM provider implementations with mocked external APIs.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from llm.provider import LLMProvider, LLMResponse, ModelInfo
from llm.ollama import OllamaProvider
from llm.anthropic_provider import AnthropicProvider
from llm.openai_provider import OpenAIProvider
from llm.hybrid import HybridRouter, TaskComplexity
from llm.config import LLMConfig, ProviderConfig


class TestLLMProvider:
    """Tests for base LLMProvider abstract class."""
    
    def test_provider_abstract(self):
        """Test that LLMProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMProvider()


class TestOllamaProvider:
    """Tests for OllamaProvider."""
    
    def test_init(self):
        """Test Ollama provider initialization."""
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            default_model="llama3.1"
        )
        assert provider.base_url == "http://localhost:11434"
        assert provider.default_model == "llama3.1"
    
    @pytest.mark.asyncio
    async def test_generate(self, mock_ollama_response):
        """Test Ollama generate method."""
        provider = OllamaProvider()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_ollama_response)
            mock_response.raise_for_status = MagicMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()
            
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            result = await provider.generate("Test prompt")
            
            assert isinstance(result, LLMResponse)
            assert result.content == "This is a test response from Ollama."
            assert result.model == "llama3.1"
            assert result.provider == "ollama"
            assert result.usage["prompt_tokens"] == 10
            assert result.usage["completion_tokens"] == 20
    
    @pytest.mark.asyncio
    async def test_stream(self, mock_ollama_response):
        """Test Ollama streaming."""
        provider = OllamaProvider()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            
            # Mock streaming response
            import json
            stream_data = [
                json.dumps({"response": "Test "}).encode(),
                json.dumps({"response": "streaming"}).encode(),
            ]
            
            async def mock_content_iter():
                for data in stream_data:
                    yield data
            
            mock_response.content = MagicMock()
            mock_response.content.__aiter__ = lambda self: mock_content_iter()
            mock_response.raise_for_status = MagicMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()
            
            mock_session.post = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            chunks = []
            async for chunk in provider.stream("Test prompt"):
                chunks.append(chunk)
            
            assert len(chunks) == 2
            assert chunks[0] == "Test "
            assert chunks[1] == "streaming"
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test Ollama health check."""
        provider = OllamaProvider()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()
            
            mock_session.get = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            result = await provider.health_check()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test listing Ollama models."""
        provider = OllamaProvider()
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value={
                "models": [
                    {"name": "llama3.1"},
                    {"name": "mistral"}
                ]
            })
            mock_response.raise_for_status = MagicMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock()
            
            mock_session.get = MagicMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            
            mock_session_class.return_value = mock_session
            
            models = await provider.list_models()
            assert "llama3.1" in models
            assert "mistral" in models


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""
    
    def test_init(self):
        """Test Anthropic provider initialization."""
        provider = AnthropicProvider(api_key="test_key")
        assert provider.api_key == "test_key"
        assert provider.default_model == "claude-3-5-sonnet-20241022"
    
    def test_init_no_key(self, monkeypatch):
        """Test initialization without API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValueError, match="Anthropic API key is required"):
            AnthropicProvider(api_key=None)
    
    @pytest.mark.asyncio
    async def test_generate(self, mock_anthropic_message):
        """Test Anthropic generate method."""
        provider = AnthropicProvider(api_key="test_key")
        
        with patch.object(provider.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_anthropic_message
            
            result = await provider.generate("Test prompt")
            
            assert isinstance(result, LLMResponse)
            assert result.content == "This is a test response from Claude."
            assert result.provider == "anthropic"
            assert result.usage["prompt_tokens"] == 10
            assert result.usage["completion_tokens"] == 20
    
    @pytest.mark.asyncio
    async def test_get_model_info(self):
        """Test getting model info."""
        provider = AnthropicProvider(api_key="test_key")
        
        info = await provider.get_model_info("claude-3-5-sonnet-20241022")
        
        assert isinstance(info, ModelInfo)
        assert info.name == "claude-3-5-sonnet-20241022"
        assert info.provider == "anthropic"
        assert info.context_window == 200000
        assert info.supports_streaming is True
    
    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test listing models."""
        provider = AnthropicProvider(api_key="test_key")
        
        models = await provider.list_models()
        
        assert "claude-opus-4-20250514" in models
        assert "claude-3-5-sonnet-20241022" in models


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""
    
    def test_init(self):
        """Test OpenAI provider initialization."""
        provider = OpenAIProvider(api_key="test_key")
        assert provider.api_key == "test_key"
        assert provider.default_model == "gpt-4o"
    
    @pytest.mark.asyncio
    async def test_generate(self, mock_openai_completion):
        """Test OpenAI generate method."""
        provider = OpenAIProvider(api_key="test_key")
        
        with patch.object(provider.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_openai_completion
            
            result = await provider.generate("Test prompt")
            
            assert isinstance(result, LLMResponse)
            assert result.content == "This is a test response from GPT-4."
            assert result.provider == "openai"
            assert result.usage["total_tokens"] == 30
    
    @pytest.mark.asyncio
    async def test_get_model_info(self):
        """Test getting model info."""
        provider = OpenAIProvider(api_key="test_key")
        
        info = await provider.get_model_info("gpt-4o")
        
        assert isinstance(info, ModelInfo)
        assert info.name == "gpt-4o"
        assert info.provider == "openai"
        assert info.context_window == 128000
        assert info.supports_function_calling is True


class TestHybridRouter:
    """Tests for HybridRouter."""
    
    @pytest.mark.asyncio
    async def test_init(self):
        """Test hybrid router initialization."""
        local = OllamaProvider()
        cloud = AnthropicProvider(api_key="test_key")
        
        router = HybridRouter(
            local_provider=local,
            cloud_provider=cloud,
            prefer_local=True
        )
        
        assert router.local_provider == local
        assert router.cloud_provider == cloud
        assert router.prefer_local is True
    
    @pytest.mark.asyncio
    async def test_estimate_complexity(self):
        """Test complexity estimation."""
        router = HybridRouter()
        
        # Simple task
        complexity = await router._estimate_complexity("What is 2+2?")
        assert complexity == TaskComplexity.SIMPLE
        
        # Complex task
        long_prompt = "Analyze and compare " * 500
        complexity = await router._estimate_complexity(long_prompt)
        assert complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting router statistics."""
        router = HybridRouter()
        
        stats = router.get_stats()
        
        assert "total_calls" in stats
        assert "local_calls" in stats
        assert "cloud_calls" in stats
        assert "estimated_cost_saved" in stats


class TestLLMConfig:
    """Tests for LLMConfig."""
    
    def test_from_env(self):
        """Test creating config from environment."""
        config = LLMConfig.from_env()
        
        assert isinstance(config, LLMConfig)
        assert config.default_provider == "anthropic"
    
    def test_get_provider_config(self):
        """Test getting provider config."""
        config = LLMConfig.from_env()
        
        ollama_config = config.get_provider_config("ollama")
        assert isinstance(ollama_config, ProviderConfig)
        assert ollama_config.enabled is True
    
    def test_is_provider_enabled(self):
        """Test checking if provider is enabled."""
        config = LLMConfig.from_env()
        
        # Anthropic should be enabled with test key
        assert config.is_provider_enabled("anthropic") is True
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        config = LLMConfig.from_env()
        
        providers = config.get_available_providers()
        assert isinstance(providers, list)
        assert "ollama" in providers
    
    def test_validate(self):
        """Test config validation."""
        config = LLMConfig.from_env()
        
        is_valid, errors = config.validate()
        # Should be valid with test environment
        assert is_valid is True
        assert len(errors) == 0
    
    def test_to_dict_masks_keys(self):
        """Test that API keys are masked in dict output."""
        config = LLMConfig.from_env()
        
        config_dict = config.to_dict()
        
        if config_dict.get("anthropic", {}).get("api_key"):
            assert config_dict["anthropic"]["api_key"] == "***MASKED***"
        if config_dict.get("openai", {}).get("api_key"):
            assert config_dict["openai"]["api_key"] == "***MASKED***"
