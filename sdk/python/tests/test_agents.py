"""Tests for agent operations."""

import pytest
from unittest.mock import Mock, patch
import httpx
from pytest_httpx import HTTPXMock
from suna_ultra import SunaClient
from suna_ultra.models import Agent
from suna_ultra.exceptions import NotFoundError, SunaError


@pytest.fixture
def client(mock_api_key):
    """Create a test client."""
    return SunaClient(api_key=mock_api_key)


def test_agent_create(client, mock_agent_response, httpx_mock: HTTPXMock):
    """Test creating an agent."""
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents",
        method="POST",
        json=mock_agent_response
    )
    
    agent = client.agents.create(
        name="Test Agent",
        type="research",
        system_prompt="You are a test agent."
    )
    
    assert isinstance(agent, Agent)
    assert agent.agent_id == "agent-123"
    assert agent.name == "Test Agent"
    assert agent.type == "research"


def test_agent_get(client, mock_agent_response, httpx_mock: HTTPXMock):
    """Test getting an agent."""
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents/agent-123",
        method="GET",
        json=mock_agent_response
    )
    
    agent = client.agents.get("agent-123")
    
    assert isinstance(agent, Agent)
    assert agent.agent_id == "agent-123"


def test_agent_get_not_found(client, httpx_mock: HTTPXMock):
    """Test getting a non-existent agent."""
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents/non-existent",
        method="GET",
        status_code=404,
        json={"detail": "Not found"}
    )
    
    with pytest.raises(NotFoundError):
        client.agents.get("non-existent")


def test_agent_list(client, mock_agent_response, httpx_mock: HTTPXMock):
    """Test listing agents."""
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents?limit=100&offset=0",
        method="GET",
        json=[mock_agent_response]
    )
    
    agents = client.agents.list()
    
    assert isinstance(agents, list)
    assert len(agents) == 1
    assert isinstance(agents[0], Agent)
    assert agents[0].agent_id == "agent-123"


def test_agent_update(client, mock_agent_response, httpx_mock: HTTPXMock):
    """Test updating an agent."""
    updated_response = {**mock_agent_response, "name": "Updated Agent"}
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents/agent-123",
        method="PUT",
        json=updated_response
    )
    
    agent = client.agents.update("agent-123", name="Updated Agent")
    
    assert isinstance(agent, Agent)
    assert agent.name == "Updated Agent"


def test_agent_delete(client, httpx_mock: HTTPXMock):
    """Test deleting an agent."""
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents/agent-123",
        method="DELETE",
        status_code=204
    )
    
    result = client.agents.delete("agent-123")
    assert result is True


def test_agent_pause(client, mock_agent_response, httpx_mock: HTTPXMock):
    """Test pausing an agent."""
    paused_response = {**mock_agent_response, "status": "paused"}
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents/agent-123/pause",
        method="POST",
        json=paused_response
    )
    
    agent = client.agents.pause("agent-123")
    assert agent.status == "paused"


def test_agent_resume(client, mock_agent_response, httpx_mock: HTTPXMock):
    """Test resuming an agent."""
    resumed_response = {**mock_agent_response, "status": "active"}
    httpx_mock.add_response(
        url="http://localhost:8000/api/agents/agent-123/resume",
        method="POST",
        json=resumed_response
    )
    
    agent = client.agents.resume("agent-123")
    assert agent.status == "active"
