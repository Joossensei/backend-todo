"""
Todo routes for the API.

This module contains all routes related to todo management.
"""

from aiohttp import web
from app.api.v1.endpoints import todos


def apply_todo_routes(routes: web.RouteTableDef) -> None:
    """Apply todo routes to the route table."""

    @routes.get("/api/v1/todos")
    async def get_todos(request: web.Request):
        """Get paginated list of todos for the authenticated user."""
        return await todos.get_todos(request)

    @routes.get("/api/v1/todo/{key}")
    async def get_todo_by_key(request: web.Request):
        """Get a specific todo by its key."""
        return await todos.get_todo_by_key(request)

    @routes.post("/api/v1/todos")
    async def create_todo(request: web.Request):
        """Create a new todo."""
        return await todos.create_todo(request)

    @routes.put("/api/v1/todo/{key}")
    async def update_todo(request: web.Request):
        """Update an existing todo."""
        return await todos.update_todo(request)

    @routes.patch("/api/v1/todo/{key}")
    async def patch_todo(request: web.Request):
        """Partially update a todo."""
        return await todos.patch_todo(request)

    @routes.delete("/api/v1/todo/{key}")
    async def delete_todo(request: web.Request):
        """Delete a todo."""
        return await todos.delete_todo(request)
