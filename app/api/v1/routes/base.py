"""
Base routes for the API.

This module contains basic routes like health checks and root endpoints.
"""

from aiohttp import web


def apply_base_routes(routes: web.RouteTableDef) -> None:
    """Apply base routes to the route table."""

    @routes.get("/")
    async def root(request: web.Request):
        """Root endpoint providing API information."""
        return web.json_response(
            {
                "message": "Welcome to Todo API",
                "version": "v1",
                "docs": "/docs",  # If you add API documentation
            }
        )

    @routes.get("/health")
    async def health(request: web.Request):
        """Health check endpoint for monitoring."""
        return web.json_response({"status": "OK", "message": "Service is running"})
