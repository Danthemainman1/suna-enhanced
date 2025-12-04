"""
Role-Based Access Control (RBAC) system for enterprise features.

Implements a hierarchical role system with the following levels:
- OWNER: Full access, can delete workspace, transfer ownership
- ADMIN: Manage users, agents, settings
- MANAGER: Create/edit agents, run tasks
- MEMBER: Run tasks, view results
- VIEWER: Read-only access
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from core.services.supabase import DBConnection
from core.utils.logger import logger
from .models import Role, RoleAssignment


# Role hierarchy (higher number = more permissions)
ROLE_HIERARCHY = {
    Role.VIEWER: 1,
    Role.MEMBER: 2,
    Role.MANAGER: 3,
    Role.ADMIN: 4,
    Role.OWNER: 5,
}


class RBACManager:
    """Manager for role-based access control operations."""
    
    def __init__(self, db: Optional[DBConnection] = None):
        """Initialize RBAC manager."""
        self.db = db or DBConnection()
    
    async def assign_role(
        self,
        user_id: UUID,
        workspace_id: UUID,
        role: Role,
        assigned_by: Optional[UUID] = None
    ) -> bool:
        """
        Assign a role to a user in a workspace.
        
        Args:
            user_id: User to assign role to
            workspace_id: Workspace ID
            role: Role to assign
            assigned_by: User who assigned the role
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            data = {
                "user_id": str(user_id),
                "workspace_id": str(workspace_id),
                "role": role.value,
                "assigned_at": datetime.utcnow().isoformat(),
            }
            
            if assigned_by:
                data["assigned_by"] = str(assigned_by)
            
            # Upsert role assignment
            await client.table("workspace_members").upsert(data).execute()
            
            logger.info(
                f"Role assigned: user={user_id}, workspace={workspace_id}, role={role.value}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            raise
    
    async def get_role(
        self,
        user_id: UUID,
        workspace_id: UUID
    ) -> Optional[Role]:
        """
        Get a user's role in a workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            
        Returns:
            User's role or None if not a member
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            result = await client.table("workspace_members")\
                .select("role")\
                .eq("user_id", str(user_id))\
                .eq("workspace_id", str(workspace_id))\
                .limit(1)\
                .execute()
            
            if result.data:
                return Role(result.data[0]["role"])
            return None
            
        except Exception as e:
            logger.error(f"Error getting role: {e}")
            return None
    
    async def check_role_level(
        self,
        user_id: UUID,
        workspace_id: UUID,
        minimum_role: Role
    ) -> bool:
        """
        Check if a user has at least the minimum required role level.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            minimum_role: Minimum required role
            
        Returns:
            True if user has sufficient role level
        """
        user_role = await self.get_role(user_id, workspace_id)
        
        if not user_role:
            return False
        
        user_level = ROLE_HIERARCHY.get(user_role, 0)
        required_level = ROLE_HIERARCHY.get(minimum_role, 0)
        
        return user_level >= required_level
    
    async def list_workspace_members(
        self,
        workspace_id: UUID
    ) -> List[RoleAssignment]:
        """
        List all members of a workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of role assignments
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            result = await client.table("workspace_members")\
                .select("*")\
                .eq("workspace_id", str(workspace_id))\
                .execute()
            
            members = []
            for row in result.data:
                members.append(RoleAssignment(
                    user_id=UUID(row["user_id"]),
                    workspace_id=UUID(row["workspace_id"]),
                    role=Role(row["role"]),
                    assigned_at=datetime.fromisoformat(row["assigned_at"]),
                    assigned_by=UUID(row["assigned_by"]) if row.get("assigned_by") else None,
                ))
            
            return members
            
        except Exception as e:
            logger.error(f"Error listing workspace members: {e}")
            raise
    
    async def transfer_ownership(
        self,
        workspace_id: UUID,
        current_owner_id: UUID,
        new_owner_id: UUID
    ) -> bool:
        """
        Transfer workspace ownership to another user.
        
        Args:
            workspace_id: Workspace ID
            current_owner_id: Current owner's user ID
            new_owner_id: New owner's user ID
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            # Verify current owner
            current_role = await self.get_role(current_owner_id, workspace_id)
            if current_role != Role.OWNER:
                raise ValueError("Current user is not the owner")
            
            # Verify new owner is a member
            new_role = await self.get_role(new_owner_id, workspace_id)
            if not new_role:
                raise ValueError("New owner is not a member of the workspace")
            
            # Update workspace owner
            await client.table("workspaces")\
                .update({"owner_id": str(new_owner_id)})\
                .eq("id", str(workspace_id))\
                .execute()
            
            # Assign OWNER role to new owner
            await self.assign_role(new_owner_id, workspace_id, Role.OWNER, current_owner_id)
            
            # Demote old owner to ADMIN
            await self.assign_role(current_owner_id, workspace_id, Role.ADMIN, new_owner_id)
            
            logger.info(
                f"Ownership transferred: workspace={workspace_id}, "
                f"from={current_owner_id}, to={new_owner_id}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error transferring ownership: {e}")
            raise
    
    async def remove_member(
        self,
        user_id: UUID,
        workspace_id: UUID
    ) -> bool:
        """
        Remove a member from a workspace.
        
        Args:
            user_id: User ID to remove
            workspace_id: Workspace ID
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            # Cannot remove owner
            role = await self.get_role(user_id, workspace_id)
            if role == Role.OWNER:
                raise ValueError("Cannot remove workspace owner")
            
            await client.table("workspace_members")\
                .delete()\
                .eq("user_id", str(user_id))\
                .eq("workspace_id", str(workspace_id))\
                .execute()
            
            logger.info(f"Member removed: user={user_id}, workspace={workspace_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing member: {e}")
            raise
