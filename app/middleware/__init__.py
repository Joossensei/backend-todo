"""
Middleware package for the AioHTTP application.

This package contains all middleware functions organized by functionality:
- error_handling: Error handling and logging middleware
- database: Database connection middleware
- authentication: Authentication and authorization middleware
- cors: CORS handling middleware
- logging: Request/response logging middleware
- rate_limit: Rate limit middleware
"""

from .error_handling import error_middleware
from .database import db_connection_middleware
from .authentication import auth_parsing_middleware
from .cors import make_cors_middleware
from .logging import request_logging_middleware
from .rate_limit import rate_limit_middleware

__all__ = [
    "error_middleware",
    "db_connection_middleware",
    "auth_parsing_middleware",
    "make_cors_middleware",
    "request_logging_middleware",
    "rate_limit_middleware",
]
