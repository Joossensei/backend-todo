from aiohttp import web
from app.services.todo_service import TodoService
from app.services.auth_service import AuthService


async def get_todos(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    page = int(request.query.get("page", 1))
    size = int(request.query.get("size", 10))
    skip = (page - 1) * size
    sort = request.query.get("sort", "incomplete-priority-desc")
    completed = request.query.get("completed")
    if completed is not None:
        completed = completed.lower() == "true"
    priority = request.query.get("priority")
    search = request.query.get("search")
    try:
        todos = await TodoService.get_todos(
            db,
            current_user["key"],
            skip=skip,
            limit=size,
            sort=sort,
            completed=completed,
            priority=priority,
            search=search,
        )
        total = await TodoService.get_total_todos(db, current_user["key"])
        todos_list = []
        for todo in todos:
            todos_list.append(
                {
                    "key": todo["key"],
                    "title": todo["title"],
                    "description": todo["description"],
                    "completed": todo["completed"],
                    "priority": todo["priority"],
                    "created_at": todo["created_at"].isoformat(),
                    "updated_at": (
                        todo["updated_at"].isoformat() if todo["updated_at"] else None
                    ),
                }
            )
        return web.json_response(
            {
                "todos": todos_list,
                "total": total,
                "page": page,
                "size": size,
                "success": True,
                "next_link": (
                    f"/api/v1/todos?page={page + 1}&size={size}&sort={sort}&completed={completed}&priority={priority}&search={search}"
                    if page * size < total
                    else None
                ),
                "prev_link": (
                    f"/api/v1/todos?page={page - 1}&size={size}&sort={sort}&completed={completed}&priority={priority}&search={search}"
                    if page > 1
                    else None
                ),
            },
            status=200,
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while getting todos (original error message: {e})",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )


async def get_todo_by_key(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise web.HTTPNotFound(
                text=f"Todo with key {key} not found",
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
        todo = await TodoService.get_todo(db, todo_id, current_user["key"])
        if not todo:
            raise web.HTTPNotFound(
                text=f"Todo with key {key} not found",
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
        return web.json_response(
            {
                "key": todo["key"],
                "title": todo["title"],
                "description": todo["description"],
                "completed": todo["completed"],
                "priority": todo["priority"],
                "created_at": todo["created_at"].isoformat(),
                "updated_at": (
                    todo["updated_at"].isoformat() if todo["updated_at"] else None
                ),
                "success": True,
            },
            status=200,
        )
    except ValueError:
        raise web.HTTPNotFound(
            text=f"Todo with key {key} not found",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while getting todo by key (original error message: {e})",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )


async def create_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    todo_data = await request.json()
    try:
        todo = await TodoService.create_todo(db, todo_data, current_user["key"])
        return web.json_response(
            {
                "key": todo["key"],
                "title": todo["title"],
                "description": todo["description"],
                "completed": todo["completed"],
                "priority": todo["priority"],
                "created_at": todo["created_at"].isoformat(),
                "updated_at": (
                    todo["updated_at"].isoformat() if todo["updated_at"] else None
                ),
                "success": True,
            },
            status=201,
        )
    except ValueError as e:
        raise web.HTTPBadRequest(
            text=str(e),
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while creating todo (original error message: {e})",
        )


async def update_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    todo_data = await request.json()
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise web.HTTPNotFound(
                text=f"Todo with key {key} not found",
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
    except ValueError:
        raise web.HTTPNotFound(
            text=f"Todo with key {key} not found",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while updating todo (original error message: {e})",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    try:
        todo = await TodoService.update_todo(
            db, todo_id, todo_data, current_user["key"]
        )
        return web.json_response(
            {
                "key": todo["key"],
                "title": todo["title"],
                "description": todo["description"],
                "completed": todo["completed"],
                "priority": todo["priority"],
                "created_at": todo["created_at"].isoformat(),
                "updated_at": (
                    todo["updated_at"].isoformat() if todo["updated_at"] else None
                ),
                "success": True,
            },
            status=200,
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while updating todo (original error message: {e})",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )


async def patch_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    todo_patch = await request.json()
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise web.HTTPNotFound(
                text=f"Todo with key {key} not found",
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
    except ValueError:
        raise web.HTTPNotFound(
            text=f"Todo with key {key} not found",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while patching todo (original error message: {e})",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    try:
        updated_todo = await TodoService.patch_todo(
            db, todo_id, todo_patch, current_user["key"]
        )
        return web.json_response(
            {
                "key": updated_todo["key"],
                "title": updated_todo["title"],
                "description": updated_todo["description"],
                "completed": updated_todo["completed"],
                "priority": updated_todo["priority"],
                "created_at": updated_todo["created_at"].isoformat(),
                "updated_at": (
                    updated_todo["updated_at"].isoformat()
                    if updated_todo["updated_at"]
                    else None
                ),
                "success": True,
            },
            status=200,
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while patching todo (original error message: {e})",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )


async def delete_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise web.HTTPNotFound(
                text=f"Todo with key {key} not found",
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
        if await TodoService.delete_todo(db, todo_id, current_user["key"]):
            return web.Response(status=204)
        else:
            raise web.HTTPInternalServerError(
                text="Internal server error while deleting todo",
                headers={
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            )
    except ValueError:
        raise web.HTTPNotFound(
            text=f"Todo with key {key} not found",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as e:
        raise web.HTTPInternalServerError(
            text=f"Internal server error while deleting todo (original error message: {e})",
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
