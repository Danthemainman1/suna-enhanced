"""Pytest configuration and fixtures for SDK tests."""

import pytest
from unittest.mock import Mock
import httpx


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "sk-test-key-12345"


@pytest.fixture
def mock_base_url():
    """Mock base URL for testing."""
    return "http://localhost:8000"


@pytest.fixture
def mock_agent_response():
    """Mock agent API response."""
    return {
        "agent_id": "agent-123",
        "name": "Test Agent",
        "type": "research",
        "status": "active",
        "capabilities": ["web_search"],
        "config": {},
        "system_prompt": "You are a test agent."
    }


@pytest.fixture
def mock_task_response():
    """Mock task API response."""
    return {
        "id": "task-456",
        "agent_id": "agent-123",
        "description": "Test task",
        "status": "pending",
        "priority": 5,
        "context": {}
    }


@pytest.fixture
def mock_task_result_response():
    """Mock task result API response."""
    return {
        "id": "result-789",
        "task_id": "task-456",
        "status": "completed",
        "output": "Task completed successfully",
        "error": None,
        "metadata": {}
    }


@pytest.fixture
def mock_workflow_response():
    """Mock workflow API response."""
    return {
        "id": "workflow-111",
        "name": "Test Workflow",
        "definition": {"steps": []},
        "status": "active"
    }


@pytest.fixture
def mock_tool_response():
    """Mock tool API response."""
    return {
        "name": "web_search",
        "description": "Search the web",
        "category": "search",
        "parameters": {}
    }
