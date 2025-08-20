from aiohttp import web
from app.services.todo_service import TodoService
from app.services.auth_service import AuthService
from app.utils.mapping import record_to_dict
from app.schemas.todo import TodoResponse, TodoListResponse, TodoCreate, TodoUpdate
from app.schemas.todo import TodoPatch
from app.utils.pagination import build_pagination_link, parse_pagination
from app.core.errors import AppError, NotFoundError, UnauthorizedError, ValidationError
import logging
from app.middleware.authentication import require_auth
from app.validators.todo_validator import (
    TodoCreateValidator,
    TodoUpdateValidator,
    TodoPatchValidator,
)
import pydantic

logger = logging.getLogger(__name__)


@require_auth()
async def get_todos(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    if not current_user:
        raise UnauthorizedError("Unauthorized")
    page, size, skip = parse_pagination(
        request.query.get("page"), request.query.get("size")
    )
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
                size=len(items),
                success=True,
                next_link=build_pagination_link(request.url, page + 1, size, total),
                prev_link=build_pagination_link(request.url, page - 1, size, total),
            ).model_dump(),
            status=200,
        )
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error getting todos: {e}")
        raise AppError(e)


@require_auth()
async def get_todo_by_key(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(f"Todo with key {key} not found")
        todo = await TodoService.get_todo(db, todo_id, current_user["key"])
        if not todo:
            raise NotFoundError(f"Todo with key {key} not found")
        return web.json_response(
            TodoResponse(**record_to_dict(todo)).model_dump(),
            status=200,
        )
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error getting todo by key: {e}")
        raise AppError(e)


@require_auth()
async def create_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    todo_data = await request.json()
    if not all(
        key in todo_data for key in ["title", "priority", "completed", "user_key"]
    ):
        raise ValidationError(custom_message="All fields are required")
    try:
        todo_model = TodoCreate(**todo_data)
        todo_model = await TodoCreateValidator.validate_todo(
            todo_model, db, current_user["key"]
        )
        todo = await TodoService.create_todo(db, todo_model, current_user["key"])
        return web.json_response(
            TodoResponse(**record_to_dict(todo)).model_dump(),
            status=201,
        )
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error creating todos: {e}")
        raise AppError(e)


@require_auth()
async def update_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    todo_data = await request.json()
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(f"Todo with key {key} not found")
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating todo: {e}")
        raise AppError(e)
    try:
        todo_model = TodoUpdate(**todo_data)
        todo_model = await TodoUpdateValidator.validate_todo(
            todo_model, db, current_user["key"]
        )
        todo = await TodoService.update_todo(
            db, todo_id, todo_model, current_user["key"]
        )
        return web.json_response(
            TodoResponse(**record_to_dict(todo)).model_dump(),
            status=200,
        )
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error updating todos: {e}")
        raise AppError(e)


@require_auth()
async def patch_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    todo_patch = await request.json()
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(f"Todo with key {key} not found")
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error patching todo: {e}")
        raise AppError(e)
    try:
        todo_model = TodoPatch(**todo_patch)
        todo_model = await TodoPatchValidator.validate_todo(
            todo_model, db, current_user["key"]
        )
        updated_todo = await TodoService.patch_todo(
            db, todo_id, todo_model, current_user["key"]
        )
        return web.json_response(
            TodoResponse(**record_to_dict(updated_todo)).model_dump(),
            status=200,
        )
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error patching todos: {e}")
        raise AppError(e)


@require_auth()
async def delete_todo(request: web.Request):
    db = request["conn"]
    username = request["user"]
    current_user = await AuthService.get_user(db, username)
    key = request.match_info["key"]
    try:
        todo_id = await TodoService.fetch_todo_id_by_key(db, key, current_user["key"])
        if not todo_id:
            raise NotFoundError(f"Todo with key {key} not found")
        if await TodoService.delete_todo(db, todo_id, current_user["key"]):
            return web.Response(status=204)
        else:
            raise AppError("Failed to delete todo")
    except UnauthorizedError as e:
        logger.error(f"Unauthorized error: {e}")
        raise UnauthorizedError(e)
    except NotFoundError as e:
        logger.error(f"Not found error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except pydantic.ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise ValidationError(e.errors())
    except Exception as e:
        logger.error(f"Error deleting todos: {e}")
        raise AppError(e)
