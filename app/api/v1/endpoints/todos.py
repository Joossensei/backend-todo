# app/api/v1/endpoints/todos.py
from aiohttp import web
from app.services.todo_service import TodoService
from app.database import get_db
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse
from app.api.deps import get_current_active_user


def setup_routes(app: web.Application, cors, prefix: str):
    """Setup todos routes."""

    # Get todos
    async def get_todos_handler(request: web.Request):
        """Get todos with pagination and filtering."""
        try:
            # Get query parameters
            page = int(request.query.get("page", 1))
            size = int(request.query.get("size", 10))
            sort = request.query.get("sort", "incomplete-priority-desc")
            completed = request.query.get("completed")
            priority = request.query.get("priority")
            search = request.query.get("search")

            if size > 100:
                return web.json_response(
                    {"detail": "Size cannot be greater than 100"}, status=400
                )

            # Get current user
            current_user = await get_current_active_user(request)

            # Get database connection
            pool = await get_db()
            async with pool.acquire() as connection:
                skip = (page - 1) * size
                todos = await TodoService.get_todos(
                    connection,
                    current_user.key,
                    skip,
                    size,
                    sort,
                    completed,
                    priority,
                    search,
                )
                total = await TodoService.get_total_todos(connection, current_user.key)

                return web.json_response(
                    TodoListResponse(
                        todos=[TodoResponse(**todo) for todo in todos],
                        total=total,
                        page=page,
                        size=len(todos),
                        success=True,
                        next_link=(
                            f"/todos?page={page + 1}&size={size}"
                            if page * size < total
                            else None
                        ),
                        prev_link=(
                            f"/todos?page={page - 1}&size={size}" if page > 1 else None
                        ),
                    ).dict()
                )

        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Get todo by key
    async def get_todo_by_key_handler(request: web.Request):
        """Get a specific todo by its key."""
        try:
            key = request.match_info["key"]
            current_user = await get_current_active_user(request)

            pool = await get_db()
            async with pool.acquire() as connection:
                todo = await TodoService.get_todo_by_key(
                    connection, key, current_user.key
                )
                if not todo:
                    return web.json_response(
                        {"detail": f"Todo with key {key} not found"}, status=404
                    )

                return web.json_response(TodoResponse(**todo).dict())

        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Create todo
    async def create_todo_handler(request: web.Request):
        """Create a new todo."""
        try:
            current_user = await get_current_active_user(request)
            data = await request.json()
            todo_create = TodoCreate(**data)

            pool = await get_db()
            async with pool.acquire() as connection:
                todo = await TodoService.create_todo(
                    connection, todo_create, current_user.key
                )
                return web.json_response(TodoResponse(**todo).dict(), status=201)

        except ValueError as e:
            return web.json_response({"detail": str(e)}, status=400)
        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Update todo
    async def update_todo_handler(request: web.Request):
        """Update a todo."""
        try:
            key = request.match_info["key"]
            current_user = await get_current_active_user(request)
            data = await request.json()
            todo_update = TodoUpdate(**data)

            pool = await get_db()
            async with pool.acquire() as connection:
                todo = await TodoService.update_todo(
                    connection, key, todo_update, current_user.key
                )
                if not todo:
                    return web.json_response(
                        {"detail": f"Todo with key {key} not found"}, status=404
                    )

                return web.json_response(TodoResponse(**todo).dict())

        except ValueError as e:
            return web.json_response({"detail": str(e)}, status=400)
        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Patch todo
    async def patch_todo_handler(request: web.Request):
        """Patch a todo."""
        try:
            key = request.match_info["key"]
            current_user = await get_current_active_user(request)
            data = await request.json()

            pool = await get_db()
            async with pool.acquire() as connection:
                todo = await TodoService.patch_todo(
                    connection, key, data, current_user.key
                )
                if not todo:
                    return web.json_response(
                        {"detail": f"Todo with key {key} not found"}, status=404
                    )

                return web.json_response(TodoResponse(**todo).dict())

        except ValueError as e:
            return web.json_response({"detail": str(e)}, status=400)
        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Delete todo
    async def delete_todo_handler(request: web.Request):
        """Delete a todo."""
        try:
            key = request.match_info["key"]
            current_user = await get_current_active_user(request)

            pool = await get_db()
            async with pool.acquire() as connection:
                success = await TodoService.delete_todo(
                    connection, key, current_user.key
                )
                if not success:
                    return web.json_response(
                        {"detail": f"Todo with key {key} not found"}, status=404
                    )

                return web.json_response({"message": "Todo deleted successfully"})

        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Add routes
    app.router.add_get(f"{prefix}", get_todos_handler)
    app.router.add_get(f"{prefix}/{{key}}", get_todo_by_key_handler)
    app.router.add_post(f"{prefix}", create_todo_handler)
    app.router.add_put(f"{prefix}/{{key}}", update_todo_handler)
    app.router.add_patch(f"{prefix}/{{key}}", patch_todo_handler)
    app.router.add_delete(f"{prefix}/{{key}}", delete_todo_handler)

    # Setup CORS for all routes
    for route in app.router.routes():
        if route.resource.canonical.startswith(prefix):
            cors.add(route)
