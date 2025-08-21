"""
Route manager for API v1.

This module provides a centralized way to register all routes for the API.
"""

from aiohttp import web
from .routes import (
    apply_base_routes,
    apply_auth_routes,
    apply_todo_routes,
    apply_priority_routes,
    apply_user_routes,
    apply_status_routes,
)


def register_all_routes() -> web.RouteTableDef:
    """
    Register all routes for the API v1.

    This function creates a route table and registers all route groups.
    The order of registration can be important for route matching.

    Returns:
        RouteTableDef with all routes registered
    """
    routes = web.RouteTableDef()

    # Register routes in logical order
    apply_base_routes(routes)  # Health checks, root
    apply_auth_routes(routes)  # Authentication
    apply_todo_routes(routes)  # Todo management
    apply_priority_routes(routes)  # Priority management
    apply_status_routes(routes)  # Status management
    apply_user_routes(routes)  # User management

    return routes


def apply_routes_to_app(app: web.Application) -> None:
    """
    Apply all routes to an AioHTTP application.

    This is a convenience function that registers all routes
    directly to an application instance.

    Args:
        app: The AioHTTP application to register routes with
    """
    routes = register_all_routes()
    app.add_routes(routes)
