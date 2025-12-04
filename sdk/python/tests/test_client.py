"""Tests for the synchronous client."""

import pytest
from unittest.mock import Mock, patch
import httpx
from suna_ultra import SunaClient
from suna_ultra.exceptions import AuthenticationError, NotFoundError


def test_client_initialization_with_api_key(mock_api_key, mock_base_url):
    """Test client initialization with API key."""
    client = SunaClient(api_key=mock_api_key, base_url=mock_base_url)
    assert client._auth.api_key == mock_api_key
    assert client._base_url == f"{mock_base_url}/api"


def test_client_initialization_without_api_key():
    """Test client initialization fails without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(AuthenticationError):
            SunaClient()


def test_client_initialization_with_env_var(mock_api_key):
    """Test client initialization with environment variable."""
    with patch.dict('os.environ', {'SUNA_API_KEY': mock_api_key}):
        client = SunaClient()
        assert client._auth.api_key == mock_api_key


def test_client_properties(mock_api_key):
    """Test client property accessors."""
    client = SunaClient(api_key=mock_api_key)
    assert client.agents is not None
    assert client.tasks is not None
    assert client.workflows is not None
    assert client.tools is not None


def test_client_context_manager(mock_api_key):
    """Test client as context manager."""
    with SunaClient(api_key=mock_api_key) as client:
        assert client._client is not None
    # Client should be closed after context exit


def test_client_close(mock_api_key):
    """Test client close method."""
    client = SunaClient(api_key=mock_api_key)
    client.close()
    # Should not raise an error
