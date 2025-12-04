"""
Pytest configuration and fixtures for Suna Ultra tests.

This module provides common fixtures and configuration for all tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, AsyncMock


# Configure pytest-asyncio
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# LLM Provider Fixtures
@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama API."""
    return {
        "response": "This is a test response from Ollama.",
        "model": "llama3.1",
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": 10,
        "eval_count": 20,
        "eval_duration": 1000000,
        "load_duration": 500000,
        "total_duration": 1500000
    }


@pytest.fixture
def mock_anthropic_message():
    """Mock message response from Anthropic API."""
    mock_msg = MagicMock()
    mock_msg.id = "msg_test123"
    mock_msg.content = [MagicMock(text="This is a test response from Claude.")]
    mock_msg.model = "claude-3-5-sonnet-20241022"
    mock_msg.stop_reason = "end_turn"
    mock_msg.stop_sequence = None
    mock_msg.usage = MagicMock(
        input_tokens=10,
        output_tokens=20
    )
    return mock_msg


@pytest.fixture
def mock_openai_completion():
    """Mock completion response from OpenAI API."""
    mock_completion = MagicMock()
    mock_completion.id = "chatcmpl-test123"
    mock_completion.model = "gpt-4o"
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(content="This is a test response from GPT-4."),
            finish_reason="stop"
        )
    ]
    mock_completion.usage = MagicMock(
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30
    )
    return mock_completion


@pytest.fixture
async def mock_ollama_client(mock_ollama_response):
    """Mock Ollama client with aiohttp session."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_ollama_response)
    mock_response.raise_for_status = MagicMock()
    
    mock_session.post = AsyncMock(return_value=mock_response.__aenter__.return_value)
    mock_session.get = AsyncMock(return_value=mock_response.__aenter__.return_value)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()
    
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock()
    
    return mock_session


@pytest.fixture
async def mock_anthropic_client(mock_anthropic_message):
    """Mock Anthropic client."""
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_anthropic_message)
    return mock_client


@pytest.fixture
async def mock_openai_client(mock_openai_completion):
    """Mock OpenAI client."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_completion)
    mock_client.models.list = AsyncMock(return_value=MagicMock(
        data=[
            MagicMock(id="gpt-4o"),
            MagicMock(id="gpt-4o-mini"),
            MagicMock(id="gpt-3.5-turbo")
        ]
    ))
    return mock_client


# Tool Fixtures
@pytest.fixture
def sample_tool_result():
    """Sample successful tool result."""
    from tools.result import ToolResult
    return ToolResult.success_result(
        output={"data": "test"},
        tool_name="test_tool",
        metadata={"test": True}
    )


@pytest.fixture
def sample_error_result():
    """Sample error tool result."""
    from tools.result import ToolResult
    return ToolResult.error_result(
        error="Test error",
        tool_name="test_tool",
        metadata={"test": True}
    )


@pytest.fixture
def tool_registry():
    """Fresh tool registry for testing."""
    from tools.registry import ToolRegistry
    return ToolRegistry()


@pytest.fixture
async def sample_tool():
    """Sample tool implementation for testing."""
    from tools.base import Tool
    from tools.result import ToolResult
    
    class TestTool(Tool):
        name = "test_tool"
        description = "A test tool"
        version = "1.0.0"
        category = "testing"
        
        async def execute(self, **kwargs) -> ToolResult:
            test_param = kwargs.get("test_param", "default")
            return ToolResult.success_result(
                output={"result": test_param},
                tool_name=self.name
            )
        
        def validate_input(self, **kwargs) -> bool:
            return True
        
        def get_capabilities(self) -> list[str]:
            return ["test_capability"]
    
    return TestTool()


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    # Set test environment variables
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "anthropic")


# Cleanup
@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Perform any necessary cleanup
    pass
