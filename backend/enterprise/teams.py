"""
Team management for enterprise features.

Manages team members, roles, and permissions within workspaces.
"""

from typing import List, Optional
from uuid import UUID
from core.services.supabase import DBConnection
from core.utils.logger import logger
from .models import TeamMemberResponse, Role
from .rbac import RBACManager
from datetime import datetime


class TeamManager:
    """Manager for team operations."""
    
    def __init__(self, db: Optional[DBConnection] = None):
        """Initialize team manager."""
        self.db = db or DBConnection()
        self.rbac_manager = RBACManager(db)
    
    async def list_members(
        self,
        workspace_id: UUID
    ) -> List[TeamMemberResponse]:
        """
        List all members of a workspace team.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of team members with their roles
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            # Get members with their roles
            result = await client.table("workspace_members")\
                .select("*, users:user_id(email, raw_user_meta_data)")\
                .eq("workspace_id", str(workspace_id))\
                .execute()
            
            members = []
            for row in result.data:
                user_data = row.get("users", {})
                meta_data = user_data.get("raw_user_meta_data", {})
                
                members.append(TeamMemberResponse(
                    user_id=UUID(row["user_id"]),
                    workspace_id=UUID(row["workspace_id"]),
                    role=Role(row["role"]),
                    email=user_data.get("email", ""),
                    name=meta_data.get("full_name") or meta_data.get("name"),
                    joined_at=datetime.fromisoformat(row["assigned_at"]),
                ))
            
            return members
            
        except Exception as e:
            logger.error(f"Error listing team members: {e}")
            raise
    
    async def update_role(
        self,
        workspace_id: UUID,
        user_id: UUID,
        new_role: Role,
        updated_by: Optional[UUID] = None
    ) -> bool:
        """
        Update a team member's role.
        
        Args:
            workspace_id: Workspace ID
            user_id: User whose role to update
            new_role: New role to assign
            updated_by: User making the change
            
        Returns:
            True if successful
        """
        try:
            # Cannot change owner role via this method
            current_role = await self.rbac_manager.get_role(user_id, workspace_id)
            if current_role == Role.OWNER:
                raise ValueError("Cannot change owner role. Use transfer_ownership instead.")
            
            # Cannot assign owner role via this method
            if new_role == Role.OWNER:
                raise ValueError("Cannot assign owner role. Use transfer_ownership instead.")
            
            # Assign new role
            await self.rbac_manager.assign_role(
                user_id,
                workspace_id,
                new_role,
                updated_by
            )
            
            logger.info(
                f"Role updated: workspace={workspace_id}, user={user_id}, "
                f"new_role={new_role.value}, by={updated_by}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error updating role: {e}")
            raise
    
    async def remove_member(
        self,
        workspace_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Remove a member from a workspace team.
        
        Cannot remove the workspace owner.
        
        Args:
            workspace_id: Workspace ID
            user_id: User to remove
            
        Returns:
            True if successful
        """
        try:
            await self.rbac_manager.remove_member(user_id, workspace_id)
            
            logger.info(f"Member removed: workspace={workspace_id}, user={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing member: {e}")
            raise
    
    async def get_member(
        self,
        workspace_id: UUID,
        user_id: UUID
    ) -> Optional[TeamMemberResponse]:
        """
        Get a specific team member.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            Team member or None if not found
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            result = await client.table("workspace_members")\
                .select("*, users:user_id(email, raw_user_meta_data)")\
                .eq("workspace_id", str(workspace_id))\
                .eq("user_id", str(user_id))\
                .limit(1)\
                .execute()
            
            if not result.data:
                return None
            
            row = result.data[0]
            user_data = row.get("users", {})
            meta_data = user_data.get("raw_user_meta_data", {})
            
            return TeamMemberResponse(
                user_id=UUID(row["user_id"]),
                workspace_id=UUID(row["workspace_id"]),
                role=Role(row["role"]),
                email=user_data.get("email", ""),
                name=meta_data.get("full_name") or meta_data.get("name"),
                joined_at=datetime.fromisoformat(row["assigned_at"]),
            )
            
        except Exception as e:
            logger.error(f"Error getting team member: {e}")
            return None
