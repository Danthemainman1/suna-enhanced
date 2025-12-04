"""
Usage tracking for enterprise features.

Tracks API calls, LLM token usage, and other metrics for billing and analytics.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from core.services.supabase import DBConnection
from core.utils.logger import logger
from .models import UsageStats


class UsageTracker:
    """Manager for usage tracking operations."""
    
    def __init__(self, db: Optional[DBConnection] = None):
        """Initialize usage tracker."""
        self.db = db or DBConnection()
    
    async def record_api_call(
        self,
        workspace_id: UUID,
        endpoint: Optional[str] = None,
        method: Optional[str] = None
    ) -> bool:
        """
        Record an API call.
        
        Args:
            workspace_id: Workspace ID
            endpoint: API endpoint called
            method: HTTP method
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            data = {
                "workspace_id": str(workspace_id),
                "metric_type": "api_call",
                "count": 1,
                "endpoint": endpoint,
                "method": method,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            await client.table("usage_metrics").insert(data).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording API call: {e}")
            # Don't raise - usage tracking failures shouldn't break requests
            return False
    
    async def record_llm_usage(
        self,
        workspace_id: UUID,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider: Optional[str] = None
    ) -> bool:
        """
        Record LLM token usage.
        
        Args:
            workspace_id: Workspace ID
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            provider: LLM provider name
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            data = {
                "workspace_id": str(workspace_id),
                "metric_type": "llm_usage",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "model": model,
                "provider": provider,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            await client.table("usage_metrics").insert(data).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording LLM usage: {e}")
            return False
    
    async def get_usage(
        self,
        workspace_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> UsageStats:
        """
        Get usage statistics for a date range.
        
        Args:
            workspace_id: Workspace ID
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Usage statistics
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            # Get API call count
            api_result = await client.table("usage_metrics")\
                .select("count", count="exact")\
                .eq("workspace_id", str(workspace_id))\
                .eq("metric_type", "api_call")\
                .gte("timestamp", start_date.isoformat())\
                .lte("timestamp", end_date.isoformat())\
                .execute()
            
            api_calls = api_result.count or 0
            
            # Get LLM usage
            llm_result = await client.table("usage_metrics")\
                .select("input_tokens, output_tokens, total_tokens")\
                .eq("workspace_id", str(workspace_id))\
                .eq("metric_type", "llm_usage")\
                .gte("timestamp", start_date.isoformat())\
                .lte("timestamp", end_date.isoformat())\
                .execute()
            
            input_tokens = sum(row.get("input_tokens", 0) for row in llm_result.data)
            output_tokens = sum(row.get("output_tokens", 0) for row in llm_result.data)
            total_tokens = sum(row.get("total_tokens", 0) for row in llm_result.data)
            
            return UsageStats(
                workspace_id=workspace_id,
                api_calls=api_calls,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                period_start=start_date,
                period_end=end_date,
            )
            
        except Exception as e:
            logger.error(f"Error getting usage: {e}")
            raise
    
    async def get_current_month(
        self,
        workspace_id: UUID
    ) -> UsageStats:
        """
        Get usage statistics for the current month.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Usage statistics for current month
        """
        now = datetime.utcnow()
        start_date = datetime(now.year, now.month, 1)
        
        # Calculate end of month
        if now.month == 12:
            end_date = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
        
        return await self.get_usage(workspace_id, start_date, end_date)
    
    async def get_daily_usage(
        self,
        workspace_id: UUID,
        date: datetime
    ) -> UsageStats:
        """
        Get usage statistics for a specific day.
        
        Args:
            workspace_id: Workspace ID
            date: Date to get usage for
            
        Returns:
            Usage statistics for the day
        """
        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
        
        return await self.get_usage(workspace_id, start_date, end_date)
    
    async def reset_usage(
        self,
        workspace_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """
        Reset usage data for a date range (admin only).
        
        Args:
            workspace_id: Workspace ID
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            await client.table("usage_metrics")\
                .delete()\
                .eq("workspace_id", str(workspace_id))\
                .gte("timestamp", start_date.isoformat())\
                .lte("timestamp", end_date.isoformat())\
                .execute()
            
            logger.info(
                f"Usage reset: workspace={workspace_id}, "
                f"range={start_date} to {end_date}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error resetting usage: {e}")
            raise
