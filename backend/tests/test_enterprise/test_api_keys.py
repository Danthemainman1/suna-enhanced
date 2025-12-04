"""
Tests for API key management.
"""

import pytest
from uuid import uuid4
from enterprise.api_keys import APIKeyManager
from datetime import datetime, timedelta


def test_generate_key():
    """Test API key generation."""
    manager = APIKeyManager()
    
    key = manager._generate_key()
    
    assert key.startswith("sk_")
    assert len(key) > 10


def test_hash_key():
    """Test API key hashing."""
    manager = APIKeyManager()
    
    key = "sk_test_key_123"
    hash1 = manager._hash_key(key)
    hash2 = manager._hash_key(key)
    
    # Same key should produce same hash
    assert hash1 == hash2
    
    # Different key should produce different hash
    hash3 = manager._hash_key("sk_different_key")
    assert hash1 != hash3


def test_mask_key():
    """Test API key masking."""
    manager = APIKeyManager()
    
    key = "sk_test_key_123"
    masked = manager._mask_key(key)
    
    assert masked == "sk_test_..."
    assert len(masked) == 11  # 8 chars + "..."


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_api_key(mock_db_connection):
    """Test creating an API key."""
    manager = APIKeyManager(mock_db_connection)
    
    workspace_id = uuid4()
    creator_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(workspace_id),
        "name": "Test Key",
        "key_hash": "hash123",
        "key_preview": "sk_test_...",
        "scopes": ["agents:read", "tasks:create"],
        "created_by": str(creator_id),
        "expires_at": None,
        "last_used_at": None,
        "created_at": "2024-01-01T00:00:00",
    }]
    
    response, plain_key = await manager.create(
        workspace_id=workspace_id,
        name="Test Key",
        scopes=["agents:read", "tasks:create"],
        created_by=creator_id,
    )
    
    assert response.name == "Test Key"
    assert plain_key.startswith("sk_")
    assert len(response.scopes) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_api_key_with_expiration(mock_db_connection):
    """Test creating an API key with expiration."""
    manager = APIKeyManager(mock_db_connection)
    
    workspace_id = uuid4()
    creator_id = uuid4()
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(workspace_id),
        "name": "Expiring Key",
        "key_hash": "hash123",
        "key_preview": "sk_test_...",
        "scopes": ["agents:read"],
        "created_by": str(creator_id),
        "expires_at": expires_at.isoformat(),
        "last_used_at": None,
        "created_at": "2024-01-01T00:00:00",
    }]
    
    response, _ = await manager.create(
        workspace_id=workspace_id,
        name="Expiring Key",
        scopes=["agents:read"],
        created_by=creator_id,
        expires_in_days=30,
    )
    
    assert response.expires_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_api_key(mock_db_connection):
    """Test validating an API key."""
    manager = APIKeyManager(mock_db_connection)
    
    plain_key = "sk_test_key_123"
    hashed_key = manager._hash_key(plain_key)
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(uuid4()),
        "key_hash": hashed_key,
        "expires_at": None,
    }]
    
    result = await manager.validate(plain_key)
    
    assert result is not None
    assert result["key_hash"] == hashed_key


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_expired_key(mock_db_connection):
    """Test that expired keys are rejected."""
    manager = APIKeyManager(mock_db_connection)
    
    plain_key = "sk_test_key_123"
    hashed_key = manager._hash_key(plain_key)
    expired_at = datetime.utcnow() - timedelta(days=1)
    
    # Mock the database response with expired key
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(uuid4()),
        "key_hash": hashed_key,
        "expires_at": expired_at.isoformat(),
    }]
    
    result = await manager.validate(plain_key)
    
    assert result is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_invalid_key(mock_db_connection):
    """Test validating an invalid key."""
    manager = APIKeyManager(mock_db_connection)
    
    # Mock empty response
    mock_db_connection.client.table().execute.return_value.data = []
    
    result = await manager.validate("sk_invalid_key")
    
    assert result is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_api_keys(mock_db_connection):
    """Test listing API keys."""
    manager = APIKeyManager(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [
        {
            "id": str(uuid4()),
            "workspace_id": str(workspace_id),
            "name": "Key 1",
            "key_preview": "sk_test_...",
            "scopes": ["agents:read"],
            "expires_at": None,
            "last_used_at": None,
            "created_at": "2024-01-01T00:00:00",
        },
        {
            "id": str(uuid4()),
            "workspace_id": str(workspace_id),
            "name": "Key 2",
            "key_preview": "sk_prod_...",
            "scopes": ["tasks:create"],
            "expires_at": None,
            "last_used_at": "2024-01-02T00:00:00",
            "created_at": "2024-01-01T00:00:00",
        }
    ]
    
    keys = await manager.list(workspace_id)
    
    assert len(keys) == 2
    assert keys[0].name == "Key 1"
    assert keys[1].name == "Key 2"
    assert keys[1].last_used_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revoke_api_key(mock_db_connection):
    """Test revoking an API key."""
    manager = APIKeyManager(mock_db_connection)
    
    key_id = uuid4()
    
    result = await manager.revoke(key_id)
    
    assert result is True


@pytest.mark.asyncio
async def test_check_rate_limit(mock_redis):
    """Test rate limiting for API keys."""
    from unittest.mock import patch
    
    manager = APIKeyManager()
    key_id = uuid4()
    
    with patch('enterprise.api_keys.redis', mock_redis):
        # First check should be allowed
        is_allowed, remaining = await manager.check_rate_limit(key_id, limit=100)
        
        assert is_allowed is True
        assert remaining >= 0


@pytest.mark.asyncio
async def test_rate_limit_exceeded(mock_redis):
    """Test when rate limit is exceeded."""
    from unittest.mock import patch
    
    manager = APIKeyManager()
    key_id = uuid4()
    
    # Mock pipeline to return count that exceeds limit
    mock_redis.client.pipeline().execute.return_value = [None, None, 101, None]
    
    with patch('enterprise.api_keys.redis', mock_redis):
        is_allowed, remaining = await manager.check_rate_limit(key_id, limit=100)
        
        assert is_allowed is False
        assert remaining == 0
