"""Exception classes for Suna Ultra SDK."""


class SunaError(Exception):
    """Base exception for all Suna Ultra SDK errors."""
    
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(SunaError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class NotFoundError(SunaError):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RateLimitError(SunaError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ValidationError(SunaError):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class TimeoutError(SunaError):
    """Raised when a request times out."""
    
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, status_code=408)


class ServerError(SunaError):
    """Raised when the server returns a 5xx error."""
    
    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__(message, status_code=status_code)


class ConflictError(SunaError):
    """Raised when there is a conflict (409)."""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)
