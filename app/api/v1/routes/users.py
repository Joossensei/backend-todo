"""
User routes for the API.

This module contains all routes related to user management.
"""

from aiohttp import web
from app.api.v1.endpoints import users


def apply_user_routes(routes: web.RouteTableDef) -> None:
    """Apply user routes to the route table."""

    @routes.get("/api/v1/users")
    async def get_users(request: web.Request):
        """Get list of users (admin only)."""
        return await users.read_users(request)

    @routes.get("/api/v1/user/{key}")
    async def get_user_by_key(request: web.Request):
        """Get a specific user by their key."""
        return await users.read_user(request)

    @routes.post("/api/v1/users")
    async def create_user(request: web.Request):
        """Create a new user."""
        return await users.create_user(request)

    @routes.put("/api/v1/user/{key}")
    async def update_user(request: web.Request):
        """Update an existing user."""
        return await users.update_user(request)

    @routes.patch("/api/v1/user/{key}")
    async def patch_user(request: web.Request):
        """Partially update an existing user."""
        return await users.patch_user(request)

    @routes.put("/api/v1/user/{key}/password")
    async def update_user_password(request: web.Request):
        """Update a user's password."""
        return await users.update_user_password(request)

    @routes.delete("/api/v1/user/{key}")
    async def delete_user(request: web.Request):
        """Delete a user."""
        return await users.delete_user(request)
