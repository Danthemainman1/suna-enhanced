"""
Audit logging system for enterprise features.

Logs all significant events including who did what, when, where (IP, user agent),
and before/after state for changes.
"""

from typing import Optional, Dict, Any, List, Literal
from uuid import UUID, uuid4
from datetime import datetime
from core.services.supabase import DBConnection
from core.utils.logger import logger
from .models import AuditEventType, AuditLogEntry, AuditLogQuery, AuditLogListResponse
import json
import csv
from io import StringIO


class AuditLog:
    """Manager for audit logging operations."""
    
    def __init__(self, db: Optional[DBConnection] = None):
        """Initialize audit log manager."""
        self.db = db or DBConnection()
    
    async def log(
        self,
        workspace_id: UUID,
        event_type: AuditEventType,
        resource_type: str,
        action: str,
        user_id: Optional[UUID] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """
        Log an audit event.
        
        Args:
            workspace_id: Workspace where event occurred
            event_type: Type of event
            resource_type: Type of resource affected
            action: Action performed
            user_id: User who performed action (optional for system actions)
            resource_id: ID of affected resource
            ip_address: IP address of requester
            user_agent: User agent string
            metadata: Additional event metadata
            before_state: State before change
            after_state: State after change
            
        Returns:
            ID of created audit log entry
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            entry_id = uuid4()
            
            # Build metadata
            full_metadata = metadata or {}
            if before_state:
                full_metadata["before_state"] = before_state
            if after_state:
                full_metadata["after_state"] = after_state
            
            data = {
                "id": str(entry_id),
                "workspace_id": str(workspace_id),
                "user_id": str(user_id) if user_id else None,
                "event_type": event_type.value,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "metadata": json.dumps(full_metadata),
                "created_at": datetime.utcnow().isoformat(),
            }
            
            await client.table("audit_logs").insert(data).execute()
            
            logger.debug(
                f"Audit log created: event={event_type.value}, "
                f"resource={resource_type}:{resource_id}, user={user_id}"
            )
            
            return entry_id
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            raise
    
    async def query(
        self,
        workspace_id: UUID,
        filters: Optional[AuditLogQuery] = None
    ) -> AuditLogListResponse:
        """
        Query audit logs with filters and pagination.
        
        Args:
            workspace_id: Workspace ID
            filters: Query filters
            
        Returns:
            Paginated list of audit log entries
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            filters = filters or AuditLogQuery()
            
            # Build query
            query = client.table("audit_logs")\
                .select("*", count="exact")\
                .eq("workspace_id", str(workspace_id))
            
            # Apply filters
            if filters.event_type:
                query = query.eq("event_type", filters.event_type.value)
            
            if filters.resource_type:
                query = query.eq("resource_type", filters.resource_type)
            
            if filters.user_id:
                query = query.eq("user_id", str(filters.user_id))
            
            if filters.start_date:
                query = query.gte("created_at", filters.start_date.isoformat())
            
            if filters.end_date:
                query = query.lte("created_at", filters.end_date.isoformat())
            
            # Apply pagination
            offset = (filters.page - 1) * filters.per_page
            query = query.order("created_at", desc=True)\
                .range(offset, offset + filters.per_page - 1)
            
            result = await query.execute()
            
            # Parse entries
            entries = []
            for row in result.data:
                metadata = json.loads(row["metadata"]) if row.get("metadata") else {}
                entries.append(AuditLogEntry(
                    id=UUID(row["id"]),
                    workspace_id=UUID(row["workspace_id"]),
                    user_id=UUID(row["user_id"]) if row.get("user_id") else None,
                    event_type=AuditEventType(row["event_type"]),
                    resource_type=row["resource_type"],
                    resource_id=row.get("resource_id"),
                    action=row["action"],
                    ip_address=row.get("ip_address"),
                    user_agent=row.get("user_agent"),
                    metadata=metadata,
                    created_at=datetime.fromisoformat(row["created_at"]),
                ))
            
            # Calculate total pages
            total = result.count or 0
            pages = (total + filters.per_page - 1) // filters.per_page
            
            return AuditLogListResponse(
                entries=entries,
                total=total,
                page=filters.page,
                per_page=filters.per_page,
                pages=pages,
            )
            
        except Exception as e:
            logger.error(f"Error querying audit logs: {e}")
            raise
    
    async def export(
        self,
        workspace_id: UUID,
        format: Literal["json", "csv"],
        filters: Optional[AuditLogQuery] = None
    ) -> str:
        """
        Export audit logs to JSON or CSV format.
        
        Args:
            workspace_id: Workspace ID
            format: Export format (json or csv)
            filters: Query filters
            
        Returns:
            Exported data as string
        """
        try:
            # Query all matching logs (ignore pagination for export)
            filters = filters or AuditLogQuery()
            filters.per_page = 10000  # Large limit for export
            
            response = await self.query(workspace_id, filters)
            
            if format == "json":
                # Convert to JSON
                entries_dict = [
                    {
                        "id": str(entry.id),
                        "workspace_id": str(entry.workspace_id),
                        "user_id": str(entry.user_id) if entry.user_id else None,
                        "event_type": entry.event_type.value,
                        "resource_type": entry.resource_type,
                        "resource_id": entry.resource_id,
                        "action": entry.action,
                        "ip_address": entry.ip_address,
                        "user_agent": entry.user_agent,
                        "metadata": entry.metadata,
                        "created_at": entry.created_at.isoformat(),
                    }
                    for entry in response.entries
                ]
                return json.dumps(entries_dict, indent=2)
            
            elif format == "csv":
                # Convert to CSV
                output = StringIO()
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "id", "workspace_id", "user_id", "event_type",
                        "resource_type", "resource_id", "action",
                        "ip_address", "user_agent", "created_at"
                    ]
                )
                writer.writeheader()
                
                for entry in response.entries:
                    writer.writerow({
                        "id": str(entry.id),
                        "workspace_id": str(entry.workspace_id),
                        "user_id": str(entry.user_id) if entry.user_id else "",
                        "event_type": entry.event_type.value,
                        "resource_type": entry.resource_type,
                        "resource_id": entry.resource_id or "",
                        "action": entry.action,
                        "ip_address": entry.ip_address or "",
                        "user_agent": entry.user_agent or "",
                        "created_at": entry.created_at.isoformat(),
                    })
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting audit logs: {e}")
            raise
