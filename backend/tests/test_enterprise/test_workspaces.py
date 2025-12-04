"""
Tests for workspace management.
"""

import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from enterprise.workspaces import WorkspaceManager, slugify
from enterprise.models import WorkspaceUpdate


def test_slugify():
    """Test slug generation."""
    assert slugify("My Workspace") == "my-workspace"
    assert slugify("Test 123!") == "test-123"
    assert slugify("  Spaces  ") == "spaces"
    assert slugify("Special@#$Chars") == "specialchars"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_workspace(mock_db_connection):
    """Test creating a workspace."""
    manager = WorkspaceManager(mock_db_connection)
    
    name = "Test Workspace"
    owner_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "name": name,
        "slug": "test-workspace",
        "description": None,
        "owner_id": str(owner_id),
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }]
    
    workspace = await manager.create(
        name=name,
        owner_id=owner_id
    )
    
    assert workspace.name == name
    assert workspace.owner_id == owner_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_workspace(mock_db_connection):
    """Test getting a workspace by ID."""
    manager = WorkspaceManager(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(workspace_id),
        "name": "Test",
        "slug": "test",
        "description": None,
        "owner_id": str(uuid4()),
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }]
    
    workspace = await manager.get(workspace_id)
    
    assert workspace is not None
    assert workspace.id == workspace_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_workspace_not_found(mock_db_connection):
    """Test getting a non-existent workspace."""
    manager = WorkspaceManager(mock_db_connection)
    
    # Mock empty response
    mock_db_connection.client.table().execute.return_value.data = []
    
    workspace = await manager.get(uuid4())
    
    assert workspace is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_workspace(mock_db_connection):
    """Test updating a workspace."""
    manager = WorkspaceManager(mock_db_connection)
    
    workspace_id = uuid4()
    updates = WorkspaceUpdate(
        name="Updated Name",
        description="Updated description"
    )
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(workspace_id),
        "name": "Updated Name",
        "slug": "test",
        "description": "Updated description",
        "owner_id": str(uuid4()),
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T01:00:00",
    }]
    
    workspace = await manager.update(workspace_id, updates)
    
    assert workspace.name == "Updated Name"
    assert workspace.description == "Updated description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_workspace(mock_db_connection):
    """Test deleting a workspace."""
    manager = WorkspaceManager(mock_db_connection)
    
    workspace_id = uuid4()
    workspace_name = "Test Workspace"
    
    # Mock get workspace response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(workspace_id),
        "name": workspace_name,
        "slug": "test-workspace",
        "description": None,
        "owner_id": str(uuid4()),
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }]
    
    result = await manager.delete(workspace_id, workspace_name)
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_workspace_wrong_confirmation(mock_db_connection):
    """Test that delete fails with wrong confirmation."""
    manager = WorkspaceManager(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock get workspace response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(workspace_id),
        "name": "Test Workspace",
        "slug": "test-workspace",
        "description": None,
        "owner_id": str(uuid4()),
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }]
    
    with pytest.raises(ValueError, match="Confirmation name does not match"):
        await manager.delete(workspace_id, "Wrong Name")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_user_workspaces(mock_db_connection):
    """Test listing workspaces for a user."""
    manager = WorkspaceManager(mock_db_connection)
    
    user_id = uuid4()
    workspace1_id = uuid4()
    workspace2_id = uuid4()
    
    # Mock workspace_members query
    mock_db_connection.client.table().execute.return_value.data = [
        {"workspace_id": str(workspace1_id)},
        {"workspace_id": str(workspace2_id)},
    ]
    
    # Mock workspaces query (called after members query)
    # We need to update the mock to return different data on subsequent calls
    workspaces_data = [
        {
            "id": str(workspace1_id),
            "name": "Workspace 1",
            "slug": "workspace-1",
            "description": None,
            "owner_id": str(user_id),
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
        {
            "id": str(workspace2_id),
            "name": "Workspace 2",
            "slug": "workspace-2",
            "description": None,
            "owner_id": str(user_id),
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
    ]
    
    # Set up mock to return workspaces on second call
    call_count = [0]
    def side_effect():
        call_count[0] += 1
        if call_count[0] == 1:
            # First call returns member data
            result = MagicMock()
            result.data = [
                {"workspace_id": str(workspace1_id)},
                {"workspace_id": str(workspace2_id)},
            ]
            return result
        else:
            # Second call returns workspace data
            result = MagicMock()
            result.data = workspaces_data
            return result
    
    mock_db_connection.client.table().execute.side_effect = side_effect
    
    workspaces = await manager.list_user_workspaces(user_id)
    
    assert len(workspaces) == 2
    assert any(w.id == workspace1_id for w in workspaces)
    assert any(w.id == workspace2_id for w in workspaces)
