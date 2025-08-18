"""
Authentication routes for the API.

This module contains routes for authentication and token management.
"""

from aiohttp import web
from app.api.v1.endpoints import token


def apply_auth_routes(routes: web.RouteTableDef) -> None:
    """Apply authentication routes to the route table."""

    @routes.post("/api/v1/token")
    async def token_route(request: web.Request):
        """Login endpoint to obtain access token."""
        return await token.login_for_access_token(request)
