"""Authentication handling for Suna Ultra SDK."""

import os
from typing import Optional
from .exceptions import AuthenticationError


class Auth:
    """Handles authentication for the Suna Ultra API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize authentication.
        
        Args:
            api_key: API key for authentication. If not provided, will try to load from SUNA_API_KEY env var.
        
        Raises:
            AuthenticationError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("SUNA_API_KEY")
        
        if not self.api_key:
            raise AuthenticationError(
                "No API key provided. Pass api_key parameter or set SUNA_API_KEY environment variable."
            )
    
    def get_headers(self) -> dict:
        """Get authentication headers for API requests."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
    
    def get_auth_header(self) -> str:
        """Get the authorization header value."""
        return self.api_key
