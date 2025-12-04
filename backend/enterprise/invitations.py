"""
Invitation management for enterprise features.

Handles inviting users to workspaces with specific roles.
"""

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from core.services.supabase import DBConnection
from core.utils.logger import logger
from .models import InvitationCreate, InvitationResponse, Role
from .rbac import RBACManager
import secrets


class InvitationManager:
    """Manager for workspace invitations."""
    
    def __init__(self, db: Optional[DBConnection] = None):
        """Initialize invitation manager."""
        self.db = db or DBConnection()
        self.rbac_manager = RBACManager(db)
    
    async def create(
        self,
        workspace_id: UUID,
        email: str,
        role: Role,
        invited_by: UUID,
        expires_in_days: int = 7
    ) -> InvitationResponse:
        """
        Create an invitation to join a workspace.
        
        Args:
            workspace_id: Workspace ID
            email: Email address to invite
            role: Role to assign when accepted
            invited_by: User creating the invitation
            expires_in_days: Days until invitation expires
            
        Returns:
            Created invitation
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            invitation_id = uuid4()
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Cannot invite as owner
            if role == Role.OWNER:
                raise ValueError("Cannot invite users as owner. Use transfer_ownership instead.")
            
            data = {
                "id": str(invitation_id),
                "workspace_id": str(workspace_id),
                "email": email.lower(),
                "role": role.value,
                "invited_by": str(invited_by),
                "token": token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
            }
            
            result = await client.table("workspace_invitations").insert(data).execute()
            
            logger.info(
                f"Invitation created: workspace={workspace_id}, email={email}, "
                f"role={role.value}, by={invited_by}"
            )
            
            return InvitationResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating invitation: {e}")
            raise
    
    async def accept(
        self,
        token: str,
        user_id: UUID
    ) -> bool:
        """
        Accept an invitation and join the workspace.
        
        Args:
            token: Invitation token
            user_id: User accepting the invitation
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            # Get invitation
            result = await client.table("workspace_invitations")\
                .select("*")\
                .eq("token", token)\
                .limit(1)\
                .execute()
            
            if not result.data:
                raise ValueError("Invalid invitation token")
            
            invitation = result.data[0]
            
            # Check if expired
            expires_at = datetime.fromisoformat(invitation["expires_at"])
            if datetime.utcnow() > expires_at:
                raise ValueError("Invitation has expired")
            
            # Add user to workspace with specified role
            workspace_id = UUID(invitation["workspace_id"])
            role = Role(invitation["role"])
            
            await self.rbac_manager.assign_role(
                user_id,
                workspace_id,
                role,
                UUID(invitation["invited_by"])
            )
            
            # Mark invitation as accepted/used
            await client.table("workspace_invitations")\
                .update({"accepted_at": datetime.utcnow().isoformat()})\
                .eq("token", token)\
                .execute()
            
            logger.info(
                f"Invitation accepted: token={token[:8]}..., user={user_id}, "
                f"workspace={workspace_id}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            raise
    
    async def revoke(
        self,
        invitation_id: UUID
    ) -> bool:
        """
        Revoke an invitation.
        
        Args:
            invitation_id: Invitation ID
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            await client.table("workspace_invitations")\
                .delete()\
                .eq("id", str(invitation_id))\
                .execute()
            
            logger.info(f"Invitation revoked: id={invitation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking invitation: {e}")
            raise
    
    async def list_pending(
        self,
        workspace_id: UUID
    ) -> List[InvitationResponse]:
        """
        List pending invitations for a workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of pending invitations
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            # Get invitations that haven't been accepted and aren't expired
            result = await client.table("workspace_invitations")\
                .select("*")\
                .eq("workspace_id", str(workspace_id))\
                .is_("accepted_at", "null")\
                .gte("expires_at", datetime.utcnow().isoformat())\
                .execute()
            
            return [InvitationResponse(**row) for row in result.data]
            
        except Exception as e:
            logger.error(f"Error listing pending invitations: {e}")
            raise
    
    async def get(
        self,
        invitation_id: UUID
    ) -> Optional[InvitationResponse]:
        """
        Get an invitation by ID.
        
        Args:
            invitation_id: Invitation ID
            
        Returns:
            Invitation or None if not found
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            result = await client.table("workspace_invitations")\
                .select("*")\
                .eq("id", str(invitation_id))\
                .limit(1)\
                .execute()
            
            if result.data:
                return InvitationResponse(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting invitation: {e}")
            return None
