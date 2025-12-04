"""
Tests for team management.
"""

import pytest
from uuid import uuid4
from enterprise.teams import TeamManager
from enterprise.models import Role


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_members(mock_db_connection):
    """Test listing team members."""
    manager = TeamManager(mock_db_connection)
    
    workspace_id = uuid4()
    user1_id = uuid4()
    user2_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [
        {
            "user_id": str(user1_id),
            "workspace_id": str(workspace_id),
            "role": "owner",
            "assigned_at": "2024-01-01T00:00:00",
            "users": {
                "email": "user1@example.com",
                "raw_user_meta_data": {"full_name": "User One"}
            }
        },
        {
            "user_id": str(user2_id),
            "workspace_id": str(workspace_id),
            "role": "member",
            "assigned_at": "2024-01-01T00:00:00",
            "users": {
                "email": "user2@example.com",
                "raw_user_meta_data": {"name": "User Two"}
            }
        }
    ]
    
    members = await manager.list_members(workspace_id)
    
    assert len(members) == 2
    assert members[0].email == "user1@example.com"
    assert members[0].role == Role.OWNER
    assert members[1].email == "user2@example.com"
    assert members[1].role == Role.MEMBER


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_role(mock_db_connection):
    """Test updating a member's role."""
    manager = TeamManager(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    # Mock get_role to return non-owner
    mock_db_connection.client.table().execute.return_value.data = [
        {"role": "member"}
    ]
    
    result = await manager.update_role(
        workspace_id,
        user_id,
        Role.MANAGER
    )
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_cannot_change_owner_role(mock_db_connection):
    """Test that owner role cannot be changed via update_role."""
    manager = TeamManager(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    # Mock get_role to return owner
    mock_db_connection.client.table().execute.return_value.data = [
        {"role": "owner"}
    ]
    
    with pytest.raises(ValueError, match="Cannot change owner role"):
        await manager.update_role(workspace_id, user_id, Role.ADMIN)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_cannot_assign_owner_role(mock_db_connection):
    """Test that owner role cannot be assigned via update_role."""
    manager = TeamManager(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    # Mock get_role to return non-owner
    mock_db_connection.client.table().execute.return_value.data = [
        {"role": "admin"}
    ]
    
    with pytest.raises(ValueError, match="Cannot assign owner role"):
        await manager.update_role(workspace_id, user_id, Role.OWNER)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_member(mock_db_connection):
    """Test removing a team member."""
    manager = TeamManager(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    result = await manager.remove_member(workspace_id, user_id)
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_member(mock_db_connection):
    """Test getting a specific team member."""
    manager = TeamManager(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "user_id": str(user_id),
        "workspace_id": str(workspace_id),
        "role": "admin",
        "assigned_at": "2024-01-01T00:00:00",
        "users": {
            "email": "admin@example.com",
            "raw_user_meta_data": {"full_name": "Admin User"}
        }
    }]
    
    member = await manager.get_member(workspace_id, user_id)
    
    assert member is not None
    assert member.user_id == user_id
    assert member.role == Role.ADMIN
    assert member.email == "admin@example.com"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_member_not_found(mock_db_connection):
    """Test getting a non-existent member."""
    manager = TeamManager(mock_db_connection)
    
    # Mock empty response
    mock_db_connection.client.table().execute.return_value.data = []
    
    member = await manager.get_member(uuid4(), uuid4())
    
    assert member is None
