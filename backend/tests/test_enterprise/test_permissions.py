"""
Tests for permissions system.
"""

import pytest
from uuid import uuid4
from enterprise.permissions import PermissionChecker, ROLE_PERMISSIONS
from enterprise.models import Role
from enterprise.rbac import RBACManager


@pytest.mark.asyncio
async def test_role_permissions_defined():
    """Test that permissions are defined for all roles."""
    for role in Role:
        assert role in ROLE_PERMISSIONS
        assert isinstance(ROLE_PERMISSIONS[role], set)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_has_permission_exact_match(mock_db_connection):
    """Test checking exact permission match."""
    rbac_manager = RBACManager(mock_db_connection)
    checker = PermissionChecker(rbac_manager)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign MANAGER role
    await rbac_manager.assign_role(user_id, workspace_id, Role.MANAGER)
    
    # Check permissions
    assert await checker.has_permission(user_id, workspace_id, "agents:create") is True
    assert await checker.has_permission(user_id, workspace_id, "agents:read") is True
    assert await checker.has_permission(user_id, workspace_id, "billing:update") is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_has_permission_wildcard(mock_db_connection):
    """Test checking permission with wildcard."""
    rbac_manager = RBACManager(mock_db_connection)
    checker = PermissionChecker(rbac_manager)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign ADMIN role (has agents:*)
    await rbac_manager.assign_role(user_id, workspace_id, Role.ADMIN)
    
    # Check wildcard permissions
    assert await checker.has_permission(user_id, workspace_id, "agents:create") is True
    assert await checker.has_permission(user_id, workspace_id, "agents:delete") is True
    assert await checker.has_permission(user_id, workspace_id, "agents:anything") is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_permissions(mock_db_connection):
    """Test getting all user permissions."""
    rbac_manager = RBACManager(mock_db_connection)
    checker = PermissionChecker(rbac_manager)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign VIEWER role
    await rbac_manager.assign_role(user_id, workspace_id, Role.VIEWER)
    
    # Get permissions
    permissions = await checker.get_user_permissions(user_id, workspace_id)
    
    assert "agents:read" in permissions
    assert "tasks:read" in permissions
    assert "agents:create" not in permissions


@pytest.mark.asyncio
@pytest.mark.integration
async def test_owner_has_all_permissions(mock_db_connection):
    """Test that OWNER has all permissions."""
    rbac_manager = RBACManager(mock_db_connection)
    checker = PermissionChecker(rbac_manager)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign OWNER role
    await rbac_manager.assign_role(user_id, workspace_id, Role.OWNER)
    
    # Check various permissions
    assert await checker.has_permission(user_id, workspace_id, "agents:create") is True
    assert await checker.has_permission(user_id, workspace_id, "billing:update") is True
    assert await checker.has_permission(user_id, workspace_id, "workspace:delete") is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_no_permission_without_membership(mock_db_connection):
    """Test that non-members have no permissions."""
    rbac_manager = RBACManager(mock_db_connection)
    checker = PermissionChecker(rbac_manager)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Don't assign any role
    
    # Check permissions
    assert await checker.has_permission(user_id, workspace_id, "agents:read") is False
    assert await checker.has_permission(user_id, workspace_id, "tasks:read") is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_check_permission_raises_on_denied(mock_db_connection):
    """Test that check_permission raises HTTPException when denied."""
    from fastapi import HTTPException
    
    rbac_manager = RBACManager(mock_db_connection)
    checker = PermissionChecker(rbac_manager)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign VIEWER role (read-only)
    await rbac_manager.assign_role(user_id, workspace_id, Role.VIEWER)
    
    # Should raise for write permission
    with pytest.raises(HTTPException) as exc_info:
        await checker.check_permission(user_id, workspace_id, "agents:create")
    
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
@pytest.mark.integration
async def test_permission_hierarchy(mock_db_connection):
    """Test that higher roles include lower role permissions."""
    rbac_manager = RBACManager(mock_db_connection)
    checker = PermissionChecker(rbac_manager)
    
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Assign ADMIN role
    await rbac_manager.assign_role(user_id, workspace_id, Role.ADMIN)
    
    # Should have all permissions from VIEWER, MEMBER, MANAGER
    assert await checker.has_permission(user_id, workspace_id, "agents:read") is True  # From VIEWER
    assert await checker.has_permission(user_id, workspace_id, "tasks:create") is True  # From MEMBER
    assert await checker.has_permission(user_id, workspace_id, "agents:update") is True  # From MANAGER
    assert await checker.has_permission(user_id, workspace_id, "team:invite") is True  # From ADMIN
