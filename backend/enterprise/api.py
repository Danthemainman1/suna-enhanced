"""
FastAPI router for enterprise features.

Provides REST API endpoints for workspaces, teams, invitations,
API keys, audit logs, and usage tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from core.utils.auth_utils import verify_and_get_user_id_from_jwt
from core.utils.logger import logger

from .models import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    TeamMemberResponse,
    UpdateRoleRequest,
    InvitationCreate,
    InvitationResponse,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyCreateResponse,
    AuditLogQuery,
    AuditLogListResponse,
    AuditEventType,
    UsageStats,
    TransferOwnershipRequest,
)
from .workspaces import WorkspaceManager
from .teams import TeamManager
from .invitations import InvitationManager
from .api_keys import APIKeyManager
from .audit_log import AuditLog
from .usage_tracking import UsageTracker
from .permissions import require_role, require_permission
from .models import Role


router = APIRouter(prefix="/enterprise", tags=["enterprise"])


# Helper to get client IP and user agent
def get_request_metadata(request: Request) -> dict:
    """Extract IP and user agent from request."""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


# Workspace Endpoints

@router.post("/workspaces", response_model=WorkspaceResponse)
async def create_workspace(
    workspace: WorkspaceCreate,
    request: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
):
    """Create a new workspace. The creator becomes the owner."""
    try:
        manager = WorkspaceManager()
        result = await manager.create(
            name=workspace.name,
            owner_id=UUID(user_id),
            slug=workspace.slug,
            description=workspace.description,
        )
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(request)
        await audit_log.log(
            workspace_id=result.id,
            event_type=AuditEventType.WORKSPACE_CREATED,
            resource_type="workspace",
            action="create",
            user_id=UUID(user_id),
            resource_id=str(result.id),
            **metadata,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces", response_model=List[WorkspaceResponse])
async def list_workspaces(
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
):
    """List all workspaces the user is a member of."""
    try:
        manager = WorkspaceManager()
        return await manager.list_user_workspaces(UUID(user_id))
        
    except Exception as e:
        logger.error(f"Error listing workspaces: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
):
    """Get workspace details."""
    try:
        manager = WorkspaceManager()
        workspace = await manager.get(workspace_id)
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        return workspace
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workspace: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    updates: WorkspaceUpdate,
    request: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Update workspace details. Requires ADMIN role."""
    try:
        manager = WorkspaceManager()
        result = await manager.update(workspace_id, updates)
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(request)
        await audit_log.log(
            workspace_id=workspace_id,
            event_type=AuditEventType.WORKSPACE_UPDATED,
            resource_type="workspace",
            action="update",
            user_id=UUID(user_id),
            resource_id=str(workspace_id),
            **metadata,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating workspace: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: UUID,
    request: TransferOwnershipRequest,
    req: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.OWNER)),
):
    """Delete a workspace. Requires OWNER role and confirmation."""
    try:
        manager = WorkspaceManager()
        await manager.delete(workspace_id, request.confirmation)
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(req)
        await audit_log.log(
            workspace_id=workspace_id,
            event_type=AuditEventType.WORKSPACE_DELETED,
            resource_type="workspace",
            action="delete",
            user_id=UUID(user_id),
            resource_id=str(workspace_id),
            **metadata,
        )
        
        return {"message": "Workspace deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting workspace: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Team Endpoints

@router.get("/workspaces/{workspace_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    workspace_id: UUID,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
):
    """List all members of a workspace team."""
    try:
        manager = TeamManager()
        return await manager.list_members(workspace_id)
        
    except Exception as e:
        logger.error(f"Error listing team members: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/workspaces/{workspace_id}/members/{member_id}/role")
async def update_member_role(
    workspace_id: UUID,
    member_id: UUID,
    role_update: UpdateRoleRequest,
    request: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Update a team member's role. Requires ADMIN role."""
    try:
        manager = TeamManager()
        await manager.update_role(
            workspace_id,
            member_id,
            role_update.role,
            UUID(user_id)
        )
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(request)
        await audit_log.log(
            workspace_id=workspace_id,
            event_type=AuditEventType.TEAM_MEMBER_ROLE_UPDATED,
            resource_type="team_member",
            action="update_role",
            user_id=UUID(user_id),
            resource_id=str(member_id),
            metadata={"new_role": role_update.role.value},
            **metadata,
        )
        
        return {"message": "Role updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating role: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/workspaces/{workspace_id}/members/{member_id}")
async def remove_team_member(
    workspace_id: UUID,
    member_id: UUID,
    request: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Remove a member from the team. Requires ADMIN role."""
    try:
        manager = TeamManager()
        await manager.remove_member(workspace_id, member_id)
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(request)
        await audit_log.log(
            workspace_id=workspace_id,
            event_type=AuditEventType.TEAM_MEMBER_REMOVED,
            resource_type="team_member",
            action="remove",
            user_id=UUID(user_id),
            resource_id=str(member_id),
            **metadata,
        )
        
        return {"message": "Member removed successfully"}
        
    except Exception as e:
        logger.error(f"Error removing member: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Invitation Endpoints

@router.post("/workspaces/{workspace_id}/invitations", response_model=InvitationResponse)
async def create_invitation(
    workspace_id: UUID,
    invitation: InvitationCreate,
    request: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Create an invitation to join the workspace. Requires ADMIN role."""
    try:
        manager = InvitationManager()
        result = await manager.create(
            workspace_id,
            invitation.email,
            invitation.role,
            UUID(user_id)
        )
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(request)
        await audit_log.log(
            workspace_id=workspace_id,
            event_type=AuditEventType.TEAM_MEMBER_ADDED,
            resource_type="invitation",
            action="create",
            user_id=UUID(user_id),
            resource_id=str(result.id),
            metadata={"email": invitation.email, "role": invitation.role.value},
            **metadata,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating invitation: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces/{workspace_id}/invitations", response_model=List[InvitationResponse])
async def list_invitations(
    workspace_id: UUID,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """List pending invitations. Requires ADMIN role."""
    try:
        manager = InvitationManager()
        return await manager.list_pending(workspace_id)
        
    except Exception as e:
        logger.error(f"Error listing invitations: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invitations/{token}/accept")
async def accept_invitation(
    token: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
):
    """Accept an invitation to join a workspace."""
    try:
        manager = InvitationManager()
        await manager.accept(token, UUID(user_id))
        
        return {"message": "Invitation accepted successfully"}
        
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/workspaces/{workspace_id}/invitations/{invitation_id}")
async def revoke_invitation(
    workspace_id: UUID,
    invitation_id: UUID,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Revoke an invitation. Requires ADMIN role."""
    try:
        manager = InvitationManager()
        await manager.revoke(invitation_id)
        
        return {"message": "Invitation revoked successfully"}
        
    except Exception as e:
        logger.error(f"Error revoking invitation: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# API Key Endpoints

@router.post("/workspaces/{workspace_id}/api-keys", response_model=APIKeyCreateResponse)
async def create_api_key(
    workspace_id: UUID,
    key_request: APIKeyCreate,
    request: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.MANAGER)),
):
    """Create a new API key. Requires MANAGER role."""
    try:
        manager = APIKeyManager()
        result, plain_key = await manager.create(
            workspace_id,
            key_request.name,
            key_request.scopes,
            UUID(user_id),
            key_request.expires_in_days
        )
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(request)
        await audit_log.log(
            workspace_id=workspace_id,
            event_type=AuditEventType.API_KEY_CREATED,
            resource_type="api_key",
            action="create",
            user_id=UUID(user_id),
            resource_id=str(result.id),
            metadata={"name": key_request.name, "scopes": key_request.scopes},
            **metadata,
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces/{workspace_id}/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    workspace_id: UUID,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.MANAGER)),
):
    """List all API keys for a workspace. Requires MANAGER role."""
    try:
        manager = APIKeyManager()
        return await manager.list(workspace_id)
        
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/workspaces/{workspace_id}/api-keys/{key_id}")
async def revoke_api_key(
    workspace_id: UUID,
    key_id: UUID,
    request: Request,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.MANAGER)),
):
    """Revoke an API key. Requires MANAGER role."""
    try:
        manager = APIKeyManager()
        await manager.revoke(key_id)
        
        # Log the event
        audit_log = AuditLog()
        metadata = get_request_metadata(request)
        await audit_log.log(
            workspace_id=workspace_id,
            event_type=AuditEventType.API_KEY_REVOKED,
            resource_type="api_key",
            action="revoke",
            user_id=UUID(user_id),
            resource_id=str(key_id),
            **metadata,
        )
        
        return {"message": "API key revoked successfully"}
        
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Audit Log Endpoints

@router.get("/workspaces/{workspace_id}/audit-logs", response_model=AuditLogListResponse)
async def query_audit_logs(
    workspace_id: UUID,
    event_type: Optional[AuditEventType] = None,
    resource_type: Optional[str] = None,
    user_id_filter: Optional[UUID] = Query(None, alias="user_id"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Query audit logs. Requires ADMIN role."""
    try:
        audit_log = AuditLog()
        filters = AuditLogQuery(
            event_type=event_type,
            resource_type=resource_type,
            user_id=user_id_filter,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page,
        )
        
        return await audit_log.query(workspace_id, filters)
        
    except Exception as e:
        logger.error(f"Error querying audit logs: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces/{workspace_id}/audit-logs/export")
async def export_audit_logs(
    workspace_id: UUID,
    format: str = Query("json", regex="^(json|csv)$"),
    event_type: Optional[AuditEventType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.ADMIN)),
):
    """Export audit logs to JSON or CSV. Requires ADMIN role."""
    try:
        audit_log = AuditLog()
        filters = AuditLogQuery(
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
        )
        
        content = await audit_log.export(workspace_id, format, filters)
        
        media_type = "application/json" if format == "json" else "text/csv"
        filename = f"audit-logs-{workspace_id}.{format}"
        
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting audit logs: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Usage Stats Endpoints

@router.get("/workspaces/{workspace_id}/usage/current", response_model=UsageStats)
async def get_current_usage(
    workspace_id: UUID,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.MEMBER)),
):
    """Get usage stats for the current month. Requires MEMBER role."""
    try:
        tracker = UsageTracker()
        return await tracker.get_current_month(workspace_id)
        
    except Exception as e:
        logger.error(f"Error getting current usage: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces/{workspace_id}/usage", response_model=UsageStats)
async def get_usage(
    workspace_id: UUID,
    start_date: datetime,
    end_date: datetime,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
    _: None = Depends(require_role(Role.MEMBER)),
):
    """Get usage stats for a date range. Requires MEMBER role."""
    try:
        tracker = UsageTracker()
        return await tracker.get_usage(workspace_id, start_date, end_date)
        
    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        raise HTTPException(status_code=400, detail=str(e))
