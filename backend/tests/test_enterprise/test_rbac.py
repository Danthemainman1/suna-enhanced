"""
Tests for RBAC (Role-Based Access Control) system.
"""

import pytest
from uuid import uuid4
from enterprise.rbac import RBACManager, ROLE_HIERARCHY
from enterprise.models import Role


@pytest.mark.asyncio
async def test_role_hierarchy():
    """Test that role hierarchy is correctly defined."""
    assert ROLE_HIERARCHY[Role.VIEWER] < ROLE_HIERARCHY[Role.MEMBER]
    assert ROLE_HIERARCHY[Role.MEMBER] < ROLE_HIERARCHY[Role.MANAGER]
    assert ROLE_HIERARCHY[Role.MANAGER] < ROLE_HIERARCHY[Role.ADMIN]
    assert ROLE_HIERARCHY[Role.ADMIN] < ROLE_HIERARCHY[Role.OWNER]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_assign_role(mock_db_connection):
    """Test assigning a role to a user."""
    manager = RBACManager(mock_db_connection)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    result = await manager.assign_role(
        user_id=user_id,
        workspace_id=workspace_id,
        role=Role.ADMIN
    )
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_role(mock_db_connection):
    """Test getting a user's role."""
    manager = RBACManager(mock_db_connection)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign role first
    await manager.assign_role(user_id, workspace_id, Role.MANAGER)
    
    # Get role
    role = await manager.get_role(user_id, workspace_id)
    
    assert role == Role.MANAGER


@pytest.mark.asyncio
@pytest.mark.integration
async def test_check_role_level(mock_db_connection):
    """Test checking if user has minimum role level."""
    manager = RBACManager(mock_db_connection)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign ADMIN role
    await manager.assign_role(user_id, workspace_id, Role.ADMIN)
    
    # Should pass for MEMBER (lower level)
    assert await manager.check_role_level(user_id, workspace_id, Role.MEMBER) is True
    
    # Should pass for ADMIN (same level)
    assert await manager.check_role_level(user_id, workspace_id, Role.ADMIN) is True
    
    # Should fail for OWNER (higher level)
    assert await manager.check_role_level(user_id, workspace_id, Role.OWNER) is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_workspace_members(mock_db_connection):
    """Test listing workspace members."""
    manager = RBACManager(mock_db_connection)
    
    workspace_id = uuid4()
    user1_id = uuid4()
    user2_id = uuid4()
    
    # Assign roles
    await manager.assign_role(user1_id, workspace_id, Role.OWNER)
    await manager.assign_role(user2_id, workspace_id, Role.MEMBER)
    
    # List members
    members = await manager.list_workspace_members(workspace_id)
    
    assert len(members) == 2
    assert any(m.user_id == user1_id and m.role == Role.OWNER for m in members)
    assert any(m.user_id == user2_id and m.role == Role.MEMBER for m in members)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_transfer_ownership(mock_db_connection):
    """Test transferring workspace ownership."""
    manager = RBACManager(mock_db_connection)
    
    workspace_id = uuid4()
    owner_id = uuid4()
    new_owner_id = uuid4()
    
    # Setup: assign roles
    await manager.assign_role(owner_id, workspace_id, Role.OWNER)
    await manager.assign_role(new_owner_id, workspace_id, Role.ADMIN)
    
    # Transfer ownership
    result = await manager.transfer_ownership(
        workspace_id=workspace_id,
        current_owner_id=owner_id,
        new_owner_id=new_owner_id
    )
    
    assert result is True
    
    # Verify new roles
    assert await manager.get_role(new_owner_id, workspace_id) == Role.OWNER
    assert await manager.get_role(owner_id, workspace_id) == Role.ADMIN


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_member(mock_db_connection):
    """Test removing a member from workspace."""
    manager = RBACManager(mock_db_connection)
    
    workspace_id = uuid4()
    user_id = uuid4()
    
    # Assign role
    await manager.assign_role(user_id, workspace_id, Role.MEMBER)
    
    # Remove member
    result = await manager.remove_member(user_id, workspace_id)
    
    assert result is True
    
    # Verify member is gone
    role = await manager.get_role(user_id, workspace_id)
    assert role is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_cannot_remove_owner(mock_db_connection):
    """Test that workspace owner cannot be removed."""
    manager = RBACManager(mock_db_connection)
    
    workspace_id = uuid4()
    owner_id = uuid4()
    
    # Assign owner role
    await manager.assign_role(owner_id, workspace_id, Role.OWNER)
    
    # Try to remove owner
    with pytest.raises(ValueError, match="Cannot remove workspace owner"):
        await manager.remove_member(owner_id, workspace_id)
