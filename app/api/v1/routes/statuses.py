"""
Status routes for the API.

This module contains all routes related to status management.
"""

from aiohttp import web
from app.api.v1.endpoints import statuses


def apply_status_routes(routes: web.RouteTableDef) -> None:
    """Apply status routes to the route table."""

    @routes.get("/api/v1/statuses")
    async def get_statuses(request: web.Request):
        """Get list of statuses for the authenticated user."""
        return await statuses.get_statuses(request)

    @routes.get("/api/v1/status/{key}")
    async def get_status_by_key(request: web.Request):
        """Get a specific status by its key."""
        return await statuses.get_status_by_key(request)

    @routes.post("/api/v1/statuses")
    async def create_status(request: web.Request):
        """Create a new status."""
        return await statuses.create_status(request)

    @routes.put("/api/v1/status/{key}")
    async def update_status(request: web.Request):
        """Update an existing status."""
        return await statuses.update_status(request)

    @routes.patch("/api/v1/status/{key}")
    async def patch_status(request: web.Request):
        """Partially update a status."""
        return await statuses.patch_status(request)

    @routes.patch("/api/v1/status/{key}/reorder")
    async def reorder_statuses(request: web.Request):
        """Reorder statuses by moving from one order position to another."""
        return await statuses.reorder_statuses(request)

    @routes.delete("/api/v1/status/{key}")
    async def delete_status(request: web.Request):
        """Delete a status."""
        return await statuses.delete_status(request)
