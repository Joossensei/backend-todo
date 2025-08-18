"""
Middleware configuration for AioHTTP application.

This module provides functions to configure and order middleware for the application.
"""

from typing import List, Callable
from aiohttp import web
from app.core.config import settings
from . import (
    make_cors_middleware,
    error_middleware,
    request_logging_middleware,
    db_connection_middleware,
    auth_parsing_middleware,
)


def get_middleware_stack() -> List[Callable]:
    """
    Get the middleware stack in the correct order.

    Middleware order is important:
    1. CORS (outermost - handles preflight requests)
    2. Error handling (catches all exceptions)
    3. Request logging (logs all requests)
    4. Database connection (provides DB connection)
    5. Authentication (innermost - validates tokens)

    Returns:
        List of middleware functions in execution order
    """
    # Create CORS middleware with configuration
    cors_middleware = make_cors_middleware(
        allowed_origins=settings.backend_cors_origins,
        allow_credentials=False,  # Set to True if using cookies/auth via browser
        strict_block=True,  # Block unknown origins with 403
        exposed_headers=["X-Request-Id"],
    )

    return [
        cors_middleware,
        error_middleware,
        request_logging_middleware,
        db_connection_middleware,
        auth_parsing_middleware,
    ]


def create_app_with_middleware() -> web.Application:
    """
    Create an AioHTTP application with all middleware configured.

    This is a convenience function that creates the app with the standard
    middleware stack. You can also use get_middleware_stack() directly
    in your app factory.

    Returns:
        Configured AioHTTP application
    """
    return web.Application(middlewares=get_middleware_stack())
