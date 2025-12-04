"""
Tests for usage tracking system.
"""

import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from enterprise.usage_tracking import UsageTracker


@pytest.mark.asyncio
@pytest.mark.integration
async def test_record_api_call(mock_db_connection):
    """Test recording an API call."""
    tracker = UsageTracker(mock_db_connection)
    
    workspace_id = uuid4()
    
    result = await tracker.record_api_call(
        workspace_id=workspace_id,
        endpoint="/api/agents",
        method="POST"
    )
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_record_llm_usage(mock_db_connection):
    """Test recording LLM token usage."""
    tracker = UsageTracker(mock_db_connection)
    
    workspace_id = uuid4()
    
    result = await tracker.record_llm_usage(
        workspace_id=workspace_id,
        model="gpt-4",
        input_tokens=100,
        output_tokens=50,
        provider="openai"
    )
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_usage(mock_db_connection):
    """Test getting usage statistics."""
    tracker = UsageTracker(mock_db_connection)
    
    workspace_id = uuid4()
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31, 23, 59, 59)
    
    # Mock API call count
    mock_db_connection.client.table().execute.return_value.count = 150
    
    # Mock LLM usage data
    mock_db_connection.client.table().execute.return_value.data = [
        {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
        {"input_tokens": 2000, "output_tokens": 1000, "total_tokens": 3000},
    ]
    
    # We need to set up different responses for different queries
    call_count = [0]
    def side_effect():
        result = MagicMock()
        call_count[0] += 1
        if call_count[0] == 1:
            # First call is for API calls
            result.count = 150
            result.data = []
        else:
            # Second call is for LLM usage
            result.count = 0
            result.data = [
                {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
                {"input_tokens": 2000, "output_tokens": 1000, "total_tokens": 3000},
            ]
        return result
    
    mock_db_connection.client.table().execute.side_effect = side_effect
    
    stats = await tracker.get_usage(workspace_id, start_date, end_date)
    
    assert stats.workspace_id == workspace_id
    assert stats.api_calls == 150
    assert stats.input_tokens == 3000
    assert stats.output_tokens == 1500
    assert stats.total_tokens == 4500


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_month(mock_db_connection):
    """Test getting current month usage."""
    tracker = UsageTracker(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock responses
    call_count = [0]
    def side_effect():
        result = MagicMock()
        call_count[0] += 1
        if call_count[0] == 1:
            result.count = 50
            result.data = []
        else:
            result.count = 0
            result.data = [
                {"input_tokens": 500, "output_tokens": 250, "total_tokens": 750},
            ]
        return result
    
    mock_db_connection.client.table().execute.side_effect = side_effect
    
    stats = await tracker.get_current_month(workspace_id)
    
    assert stats.workspace_id == workspace_id
    assert stats.api_calls == 50
    assert stats.input_tokens == 500


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_daily_usage(mock_db_connection):
    """Test getting daily usage."""
    tracker = UsageTracker(mock_db_connection)
    
    workspace_id = uuid4()
    date = datetime(2024, 1, 15)
    
    # Mock responses
    call_count = [0]
    def side_effect():
        result = MagicMock()
        call_count[0] += 1
        if call_count[0] == 1:
            result.count = 10
            result.data = []
        else:
            result.count = 0
            result.data = [
                {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
            ]
        return result
    
    mock_db_connection.client.table().execute.side_effect = side_effect
    
    stats = await tracker.get_daily_usage(workspace_id, date)
    
    assert stats.workspace_id == workspace_id
    assert stats.api_calls == 10
    assert stats.period_start.date() == date.date()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reset_usage(mock_db_connection):
    """Test resetting usage data."""
    tracker = UsageTracker(mock_db_connection)
    
    workspace_id = uuid4()
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31, 23, 59, 59)
    
    result = await tracker.reset_usage(workspace_id, start_date, end_date)
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_record_api_call_failure_doesnt_raise(mock_db_connection):
    """Test that recording failures don't break the request."""
    tracker = UsageTracker(mock_db_connection)
    
    # Mock failure
    mock_db_connection.client.table().execute.side_effect = Exception("DB error")
    
    workspace_id = uuid4()
    
    # Should not raise exception
    result = await tracker.record_api_call(workspace_id)
    
    # Should return False but not crash
    assert result is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_zero_usage(mock_db_connection):
    """Test getting usage when there is none."""
    tracker = UsageTracker(mock_db_connection)
    
    workspace_id = uuid4()
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    # Mock empty responses
    call_count = [0]
    def side_effect():
        result = MagicMock()
        call_count[0] += 1
        result.count = 0
        result.data = []
        return result
    
    mock_db_connection.client.table().execute.side_effect = side_effect
    
    stats = await tracker.get_usage(workspace_id, start_date, end_date)
    
    assert stats.api_calls == 0
    assert stats.input_tokens == 0
    assert stats.output_tokens == 0
    assert stats.total_tokens == 0
