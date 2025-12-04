"""
Pytest fixtures for enterprise tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing."""
    mock_db = MagicMock()
    mock_db.initialize = AsyncMock()
    mock_db.client = MagicMock()
    
    # Mock table operations
    mock_table = MagicMock()
    mock_table.select = MagicMock(return_value=mock_table)
    mock_table.insert = MagicMock(return_value=mock_table)
    mock_table.update = MagicMock(return_value=mock_table)
    mock_table.delete = MagicMock(return_value=mock_table)
    mock_table.upsert = MagicMock(return_value=mock_table)
    mock_table.eq = MagicMock(return_value=mock_table)
    mock_table.in_ = MagicMock(return_value=mock_table)
    mock_table.is_ = MagicMock(return_value=mock_table)
    mock_table.gte = MagicMock(return_value=mock_table)
    mock_table.lte = MagicMock(return_value=mock_table)
    mock_table.limit = MagicMock(return_value=mock_table)
    mock_table.order = MagicMock(return_value=mock_table)
    mock_table.range = MagicMock(return_value=mock_table)
    
    # Mock execute
    mock_execute_result = MagicMock()
    mock_execute_result.data = []
    mock_execute_result.count = 0
    mock_table.execute = AsyncMock(return_value=mock_execute_result)
    
    mock_db.client.table = MagicMock(return_value=mock_table)
    
    return mock_db


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    mock_redis = MagicMock()
    mock_redis.initialize_async = AsyncMock()
    mock_redis.client = MagicMock()
    mock_redis.client.pipeline = MagicMock()
    
    # Mock pipeline
    mock_pipeline = MagicMock()
    mock_pipeline.zremrangebyscore = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zadd = MagicMock(return_value=mock_pipeline)
    mock_pipeline.zcard = MagicMock(return_value=mock_pipeline)
    mock_pipeline.expire = MagicMock(return_value=mock_pipeline)
    mock_pipeline.execute = AsyncMock(return_value=[None, None, 0, None])
    
    mock_redis.client.pipeline.return_value = mock_pipeline
    
    return mock_redis
