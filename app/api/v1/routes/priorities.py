"""
Priority routes for the API.

This module contains all routes related to priority management.
"""

from aiohttp import web
from app.api.v1.endpoints import priorities


def apply_priority_routes(routes: web.RouteTableDef) -> None:
    """Apply priority routes to the route table."""

    @routes.get("/api/v1/priorities")
    async def get_priorities(request: web.Request):
        """Get list of priorities for the authenticated user."""
        return await priorities.get_priorities(request)

    @routes.get("/api/v1/priority/{key}")
    async def get_priority_by_key(request: web.Request):
        """Get a specific priority by its key."""
        return await priorities.get_priority_by_key(request)

    @routes.post("/api/v1/priorities")
    async def create_priority(request: web.Request):
        """Create a new priority."""
        return await priorities.create_priority(request)

    @routes.put("/api/v1/priority/{key}")
    async def update_priority(request: web.Request):
        """Update an existing priority."""
        return await priorities.update_priority(request)

    @routes.patch("/api/v1/priority/{key}")
    async def patch_priority(request: web.Request):
        """Partially update a priority."""
        return await priorities.patch_priority(request)

    @routes.delete("/api/v1/priority/{key}")
    async def delete_priority(request: web.Request):
        """Delete a priority."""
        return await priorities.delete_priority(request)
