"""
API key management for enterprise features.

Manages API keys for programmatic access with rate limiting.
"""

from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from core.services.supabase import DBConnection
from core.utils.logger import logger
from .models import APIKeyCreate, APIKeyResponse, APIKeyCreateResponse
import secrets
import hashlib
import time


class APIKeyManager:
    """Manager for API key operations."""
    
    def __init__(self, db: Optional[DBConnection] = None):
        """Initialize API key manager."""
        self.db = db or DBConnection()
    
    def _generate_key(self) -> str:
        """Generate a secure API key."""
        return f"sk_{secrets.token_urlsafe(32)}"
    
    def _hash_key(self, plain_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(plain_key.encode()).hexdigest()
    
    def _mask_key(self, plain_key: str) -> str:
        """Create a masked preview of the key."""
        return f"{plain_key[:8]}..."
    
    async def create(
        self,
        workspace_id: UUID,
        name: str,
        scopes: List[str],
        created_by: UUID,
        expires_in_days: Optional[int] = None
    ) -> Tuple[APIKeyCreateResponse, str]:
        """
        Create a new API key.
        
        Args:
            workspace_id: Workspace ID
            name: Name/description of the key
            scopes: List of permission scopes
            created_by: User creating the key
            expires_in_days: Days until key expires (None for no expiration)
            
        Returns:
            Tuple of (key info, plain key) - plain key is only shown once!
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            key_id = uuid4()
            plain_key = self._generate_key()
            hashed_key = self._hash_key(plain_key)
            
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            data = {
                "id": str(key_id),
                "workspace_id": str(workspace_id),
                "name": name,
                "key_hash": hashed_key,
                "key_preview": self._mask_key(plain_key),
                "scopes": scopes,
                "created_by": str(created_by),
                "expires_at": expires_at.isoformat() if expires_at else None,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            result = await client.table("api_keys").insert(data).execute()
            
            logger.info(
                f"API key created: id={key_id}, workspace={workspace_id}, "
                f"name={name}, by={created_by}"
            )
            
            response = APIKeyCreateResponse(
                id=key_id,
                workspace_id=workspace_id,
                name=name,
                key=plain_key,  # Only shown once!
                scopes=scopes,
                expires_at=expires_at,
                created_at=datetime.fromisoformat(result.data[0]["created_at"]),
            )
            
            return response, plain_key
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            raise
    
    async def validate(
        self,
        plain_key: str
    ) -> Optional[dict]:
        """
        Validate an API key and return its details.
        
        Args:
            plain_key: Plain text API key
            
        Returns:
            Key details if valid, None otherwise
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            hashed_key = self._hash_key(plain_key)
            
            result = await client.table("api_keys")\
                .select("*")\
                .eq("key_hash", hashed_key)\
                .limit(1)\
                .execute()
            
            if not result.data:
                return None
            
            key_data = result.data[0]
            
            # Check if expired
            if key_data.get("expires_at"):
                expires_at = datetime.fromisoformat(key_data["expires_at"])
                if datetime.utcnow() > expires_at:
                    logger.warning(f"Expired API key used: id={key_data['id']}")
                    return None
            
            # Update last used timestamp
            await client.table("api_keys")\
                .update({"last_used_at": datetime.utcnow().isoformat()})\
                .eq("id", key_data["id"])\
                .execute()
            
            return key_data
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    async def list(
        self,
        workspace_id: UUID
    ) -> List[APIKeyResponse]:
        """
        List all API keys for a workspace (with masked keys).
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of API keys
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            result = await client.table("api_keys")\
                .select("*")\
                .eq("workspace_id", str(workspace_id))\
                .order("created_at", desc=True)\
                .execute()
            
            keys = []
            for row in result.data:
                keys.append(APIKeyResponse(
                    id=UUID(row["id"]),
                    workspace_id=UUID(row["workspace_id"]),
                    name=row["name"],
                    key_preview=row["key_preview"],
                    scopes=row["scopes"],
                    expires_at=datetime.fromisoformat(row["expires_at"]) if row.get("expires_at") else None,
                    last_used_at=datetime.fromisoformat(row["last_used_at"]) if row.get("last_used_at") else None,
                    created_at=datetime.fromisoformat(row["created_at"]),
                ))
            
            return keys
            
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            raise
    
    async def revoke(
        self,
        key_id: UUID
    ) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: API key ID
            
        Returns:
            True if successful
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            await client.table("api_keys")\
                .delete()\
                .eq("id", str(key_id))\
                .execute()
            
            logger.info(f"API key revoked: id={key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            raise
    
    async def check_rate_limit(
        self,
        key_id: UUID,
        limit: int = 1000,
        window_seconds: int = 3600
    ) -> Tuple[bool, int]:
        """
        Check if an API key has exceeded its rate limit using Redis.
        
        Args:
            key_id: API key ID
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        try:
            from core.services import redis
            
            # Initialize Redis if needed
            await redis.initialize_async()
            
            cache_key = f"rate_limit:api_key:{key_id}"
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Use Redis sorted set for sliding window rate limiting
            pipe = redis.client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(cache_key, 0, window_start)
            
            # Add current request
            pipe.zadd(cache_key, {str(current_time): current_time})
            
            # Count requests in window
            pipe.zcard(cache_key)
            
            # Set expiration
            pipe.expire(cache_key, window_seconds)
            
            results = await pipe.execute()
            count = results[2]  # Result from zcard
            
            remaining = max(0, limit - count)
            is_allowed = count <= limit
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded: key_id={key_id}, count={count}, limit={limit}"
                )
            
            return is_allowed, remaining
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Allow request on error (fail open)
            return True, limit
