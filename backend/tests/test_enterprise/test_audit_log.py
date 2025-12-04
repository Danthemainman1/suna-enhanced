"""
Tests for audit logging system.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from enterprise.audit_log import AuditLog
from enterprise.models import AuditEventType, AuditLogQuery


@pytest.mark.asyncio
@pytest.mark.integration
async def test_log_event(mock_db_connection):
    """Test logging an audit event."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    entry_id = await audit_log.log(
        workspace_id=workspace_id,
        event_type=AuditEventType.AGENT_CREATED,
        resource_type="agent",
        action="create",
        user_id=user_id,
        resource_id="agent-123",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
    )
    
    assert entry_id is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_log_with_state_changes(mock_db_connection):
    """Test logging with before/after state."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    before_state = {"name": "Old Name", "status": "active"}
    after_state = {"name": "New Name", "status": "active"}
    
    entry_id = await audit_log.log(
        workspace_id=workspace_id,
        event_type=AuditEventType.AGENT_UPDATED,
        resource_type="agent",
        action="update",
        user_id=user_id,
        resource_id="agent-123",
        before_state=before_state,
        after_state=after_state,
    )
    
    assert entry_id is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_audit_logs(mock_db_connection):
    """Test querying audit logs."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [
        {
            "id": str(uuid4()),
            "workspace_id": str(workspace_id),
            "user_id": str(uuid4()),
            "event_type": "agent.created",
            "resource_type": "agent",
            "resource_id": "agent-1",
            "action": "create",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "metadata": "{}",
            "created_at": "2024-01-01T00:00:00",
        },
        {
            "id": str(uuid4()),
            "workspace_id": str(workspace_id),
            "user_id": str(uuid4()),
            "event_type": "task.created",
            "resource_type": "task",
            "resource_id": "task-1",
            "action": "create",
            "ip_address": "192.168.1.2",
            "user_agent": "Mozilla/5.0",
            "metadata": "{}",
            "created_at": "2024-01-01T01:00:00",
        }
    ]
    mock_db_connection.client.table().execute.return_value.count = 2
    
    response = await audit_log.query(workspace_id)
    
    assert len(response.entries) == 2
    assert response.total == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_with_filters(mock_db_connection):
    """Test querying with filters."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    filters = AuditLogQuery(
        event_type=AuditEventType.AGENT_CREATED,
        user_id=user_id,
        page=1,
        per_page=10,
    )
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(workspace_id),
        "user_id": str(user_id),
        "event_type": "agent.created",
        "resource_type": "agent",
        "resource_id": "agent-1",
        "action": "create",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "metadata": "{}",
        "created_at": "2024-01-01T00:00:00",
    }]
    mock_db_connection.client.table().execute.return_value.count = 1
    
    response = await audit_log.query(workspace_id, filters)
    
    assert len(response.entries) == 1
    assert response.entries[0].event_type == AuditEventType.AGENT_CREATED


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_with_pagination(mock_db_connection):
    """Test pagination in queries."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    
    filters = AuditLogQuery(
        page=2,
        per_page=25,
    )
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = []
    mock_db_connection.client.table().execute.return_value.count = 75
    
    response = await audit_log.query(workspace_id, filters)
    
    assert response.page == 2
    assert response.per_page == 25
    assert response.total == 75
    assert response.pages == 3  # 75 / 25 = 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_export_json(mock_db_connection):
    """Test exporting audit logs as JSON."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(workspace_id),
        "user_id": str(uuid4()),
        "event_type": "agent.created",
        "resource_type": "agent",
        "resource_id": "agent-1",
        "action": "create",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "metadata": "{}",
        "created_at": "2024-01-01T00:00:00",
    }]
    mock_db_connection.client.table().execute.return_value.count = 1
    
    result = await audit_log.export(workspace_id, "json")
    
    assert isinstance(result, str)
    assert "agent.created" in result
    assert "agent-1" in result


@pytest.mark.asyncio
@pytest.mark.integration
async def test_export_csv(mock_db_connection):
    """Test exporting audit logs as CSV."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(workspace_id),
        "user_id": str(uuid4()),
        "event_type": "agent.created",
        "resource_type": "agent",
        "resource_id": "agent-1",
        "action": "create",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "metadata": "{}",
        "created_at": "2024-01-01T00:00:00",
    }]
    mock_db_connection.client.table().execute.return_value.count = 1
    
    result = await audit_log.export(workspace_id, "csv")
    
    assert isinstance(result, str)
    assert "id,workspace_id,user_id" in result
    assert "agent.created" in result
    assert "agent-1" in result


@pytest.mark.asyncio
@pytest.mark.integration
async def test_export_invalid_format(mock_db_connection):
    """Test that invalid export format raises error."""
    audit_log = AuditLog(mock_db_connection)
    
    workspace_id = uuid4()
    
    with pytest.raises(ValueError, match="Unsupported format"):
        await audit_log.export(workspace_id, "xml")
