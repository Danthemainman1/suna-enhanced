"""
Tests for invitation management.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from enterprise.invitations import InvitationManager
from enterprise.models import Role


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_invitation(mock_db_connection):
    """Test creating an invitation."""
    manager = InvitationManager(mock_db_connection)
    
    workspace_id = uuid4()
    inviter_id = uuid4()
    email = "newuser@example.com"
    
    # Mock the database response
    invitation_id = uuid4()
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(invitation_id),
        "workspace_id": str(workspace_id),
        "email": email,
        "role": "member",
        "invited_by": str(inviter_id),
        "token": "test_token_123",
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }]
    
    invitation = await manager.create(
        workspace_id=workspace_id,
        email=email,
        role=Role.MEMBER,
        invited_by=inviter_id
    )
    
    assert invitation.id == invitation_id
    assert invitation.email == email
    assert invitation.role == Role.MEMBER


@pytest.mark.asyncio
@pytest.mark.integration
async def test_cannot_invite_as_owner(mock_db_connection):
    """Test that users cannot be invited as owner."""
    manager = InvitationManager(mock_db_connection)
    
    workspace_id = uuid4()
    inviter_id = uuid4()
    
    with pytest.raises(ValueError, match="Cannot invite users as owner"):
        await manager.create(
            workspace_id=workspace_id,
            email="user@example.com",
            role=Role.OWNER,
            invited_by=inviter_id
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_accept_invitation(mock_db_connection):
    """Test accepting an invitation."""
    manager = InvitationManager(mock_db_connection)
    
    token = "test_token_123"
    user_id = uuid4()
    workspace_id = uuid4()
    
    # Mock get invitation response
    mock_db_connection.client.table().execute.return_value.data = [{
        "workspace_id": str(workspace_id),
        "role": "admin",
        "invited_by": str(uuid4()),
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }]
    
    result = await manager.accept(token, user_id)
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_accept_invalid_token(mock_db_connection):
    """Test accepting with invalid token."""
    manager = InvitationManager(mock_db_connection)
    
    # Mock empty response
    mock_db_connection.client.table().execute.return_value.data = []
    
    with pytest.raises(ValueError, match="Invalid invitation token"):
        await manager.accept("invalid_token", uuid4())


@pytest.mark.asyncio
@pytest.mark.integration
async def test_accept_expired_invitation(mock_db_connection):
    """Test that expired invitations cannot be accepted."""
    manager = InvitationManager(mock_db_connection)
    
    token = "test_token_123"
    user_id = uuid4()
    
    # Mock invitation that expired yesterday
    mock_db_connection.client.table().execute.return_value.data = [{
        "workspace_id": str(uuid4()),
        "role": "member",
        "invited_by": str(uuid4()),
        "expires_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
    }]
    
    with pytest.raises(ValueError, match="Invitation has expired"):
        await manager.accept(token, user_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revoke_invitation(mock_db_connection):
    """Test revoking an invitation."""
    manager = InvitationManager(mock_db_connection)
    
    invitation_id = uuid4()
    
    result = await manager.revoke(invitation_id)
    
    assert result is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_pending_invitations(mock_db_connection):
    """Test listing pending invitations."""
    manager = InvitationManager(mock_db_connection)
    
    workspace_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [
        {
            "id": str(uuid4()),
            "workspace_id": str(workspace_id),
            "email": "user1@example.com",
            "role": "member",
            "invited_by": str(uuid4()),
            "token": "token1",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": str(uuid4()),
            "workspace_id": str(workspace_id),
            "email": "user2@example.com",
            "role": "admin",
            "invited_by": str(uuid4()),
            "token": "token2",
            "expires_at": (datetime.utcnow() + timedelta(days=5)).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        }
    ]
    
    invitations = await manager.list_pending(workspace_id)
    
    assert len(invitations) == 2
    assert invitations[0].email == "user1@example.com"
    assert invitations[1].email == "user2@example.com"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_invitation(mock_db_connection):
    """Test getting an invitation by ID."""
    manager = InvitationManager(mock_db_connection)
    
    invitation_id = uuid4()
    workspace_id = uuid4()
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(invitation_id),
        "workspace_id": str(workspace_id),
        "email": "user@example.com",
        "role": "manager",
        "invited_by": str(uuid4()),
        "token": "test_token",
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }]
    
    invitation = await manager.get(invitation_id)
    
    assert invitation is not None
    assert invitation.id == invitation_id
    assert invitation.email == "user@example.com"
    assert invitation.role == Role.MANAGER


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_invitation_not_found(mock_db_connection):
    """Test getting a non-existent invitation."""
    manager = InvitationManager(mock_db_connection)
    
    # Mock empty response
    mock_db_connection.client.table().execute.return_value.data = []
    
    invitation = await manager.get(uuid4())
    
    assert invitation is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_custom_expiration(mock_db_connection):
    """Test creating invitation with custom expiration."""
    manager = InvitationManager(mock_db_connection)
    
    workspace_id = uuid4()
    inviter_id = uuid4()
    expires_at = datetime.utcnow() + timedelta(days=14)
    
    # Mock the database response
    mock_db_connection.client.table().execute.return_value.data = [{
        "id": str(uuid4()),
        "workspace_id": str(workspace_id),
        "email": "user@example.com",
        "role": "member",
        "invited_by": str(inviter_id),
        "token": "test_token",
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }]
    
    invitation = await manager.create(
        workspace_id=workspace_id,
        email="user@example.com",
        role=Role.MEMBER,
        invited_by=inviter_id,
        expires_in_days=14
    )
    
    assert invitation is not None
