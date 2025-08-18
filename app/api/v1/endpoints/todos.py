from aiohttp import web
from app.services.todo_service import TodoService
from app.services.auth_service import AuthService
from app.utils.mapping import record_to_dict
from app.schemas.todo import TodoResponse, TodoListResponse
from app.utils.pagination import build_pagination_link
from app.core.errors import AppError, NotFoundError
import logging

logger = logging.getLogger(__name__)


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
        items = [TodoResponse(**record_to_dict(t)) for t in todos]
        return web.json_response(
            TodoListResponse(
                todos=items,
                total=total,
                page=page,
                size=size,
                success=True,
                next_link=build_pagination_link(request.url, page + 1, size, total),
                prev_link=build_pagination_link(request.url, page - 1, size, total),
            ).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


async def get_todo_by_key(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(ValueError(f"Todo with key {key} not found"))
        todo = await TodoService.get_todo(db, todo_id, current_user["key"])
        if not todo:
            raise NotFoundError(ValueError(f"Todo with key {key} not found"))
        return web.json_response(
            TodoResponse(**record_to_dict(todo)).model_dump(),
            status=200,
        )
    except ValueError:
        raise NotFoundError(ValueError(f"Todo with key {key} not found"))
    except Exception as e:
        raise AppError(e)


async def create_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    todo_data = await request.json()
    try:
        todo = await TodoService.create_todo(db, todo_data, current_user["key"])
        return web.json_response(
            TodoResponse(**record_to_dict(todo)).model_dump(),
            status=201,
        )
    except ValueError as e:
        raise AppError(e)
    except Exception as e:
        raise AppError(e)


async def update_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    todo_data = await request.json()
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(ValueError(f"Todo with key {key} not found"))
    except ValueError:
        raise NotFoundError(ValueError(f"Todo with key {key} not found"))
    except Exception as e:
        raise AppError(e)
    try:
        todo = await TodoService.update_todo(
            db, todo_id, todo_data, current_user["key"]
        )
        return web.json_response(
            TodoResponse(**record_to_dict(todo)).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


async def patch_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    todo_patch = await request.json()
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(ValueError(f"Todo with key {key} not found"))
    except ValueError:
        raise NotFoundError(ValueError(f"Todo with key {key} not found"))
    except Exception as e:
        raise AppError(e)
    try:
        updated_todo = await TodoService.patch_todo(
            db, todo_id, todo_patch, current_user["key"]
        )
        return web.json_response(
            TodoResponse(**record_to_dict(updated_todo)).model_dump(),
            status=200,
        )
    except Exception as e:
        raise AppError(e)


async def delete_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(ValueError(f"Todo with key {key} not found"))
        if await TodoService.delete_todo(db, todo_id, current_user["key"]):
            return web.Response(status=204)
        else:
            raise AppError(ValueError("Failed to delete todo"))
    except ValueError:
        raise NotFoundError(ValueError(f"Todo with key {key} not found"))
    except Exception as e:
        raise AppError(e)
