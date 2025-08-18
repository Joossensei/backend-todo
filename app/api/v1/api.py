"""
API v1 module.

This module provides the main API interface for version 1 of the Todo API.
It uses the route manager to register all routes in a clean, organized way.
"""

from aiohttp import web
from .route_manager import register_all_routes


def apply_endpoints(routes: web.RouteTableDef):
    """
    Apply all API v1 endpoints to the given route table.

    This function is kept for backward compatibility but now delegates
    to the route manager for better organization.

    Args:
        routes: The route table to register endpoints with

    Returns:
        The route table with all endpoints registered
    """
    # Get all routes from the route manager
    all_routes = register_all_routes()

    # Copy all routes to the provided route table
    for route in all_routes:
        routes._items.append(route)

    return routes
